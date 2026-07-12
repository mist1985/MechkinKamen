/* ============================================================
   ADS — interstitials at the battle's edges, never inside it.

   OFF FOR v1, AND THE SDK IS NOT EVEN INSTALLED. Merely linking the AdMob
   library makes Android request ACCESS_ADSERVICES_AD_ID / _ATTRIBUTION /
   _TOPICS, which obliges a Play Data-safety declaration that the app collects an
   advertising identifier — untrue while ads are off. So v1 ships without the SDK
   and this file degrades to a no-op (Capacitor.Plugins.AdMob is undefined).

   TO TURN ADS ON:
     1. npm install @capacitor-community/admob
     2. In android/app/src/main/AndroidManifest.xml add back:
          <uses-permission android:name="com.google.android.gms.permission.AD_ID" />
          <meta-data android:name="com.google.android.gms.ads.APPLICATION_ID"
                     android:value="YOUR-REAL-ADMOB-APP-ID" />
     3. Set ADS_ENABLED = true and put your real unit id in INTERSTITIAL_ID.
     4. Set USE_TEST_ADS = false only when you are ready to serve live ads.
     5. Declare the advertising id on the Play Data-safety form.
     6. npx cap sync android

   Never click your own live ads — that is the quickest route to a permanently
   terminated AdMob account. Stay on the test ids until you ship.
   ============================================================ */
(function () {
  'use strict';

  const ADS_ENABLED = false;

  // Google's public test unit: always fills, earns nothing.
  const INTERSTITIAL_ID = 'ca-app-pub-3940256099942544/1033173712';
  const USE_TEST_ADS = true;

  // An ad that has not loaded in this long is abandoned; the game starts anyway.
  const LOAD_TIMEOUT_MS = 4000;
  // Two ads inside a minute reads as spam and hurts retention more than it earns.
  const MIN_GAP_MS = 60000;

  const AdMob = window.Capacitor?.Plugins?.AdMob;
  const isNative = ADS_ENABLED && !!AdMob && window.Capacitor?.isNativePlatform?.();

  let ready = false;
  let lastShown = 0;
  let gamesPlayed = 0;

  const idle = () => new Promise((r) => setTimeout(r, 0));

  /** Resolves false rather than throwing — an ad failure must never break play. */
  function withTimeout(promise, ms) {
    return Promise.race([
      promise.then(() => true).catch(() => false),
      new Promise((r) => setTimeout(() => r(false), ms)),
    ]);
  }

  async function init() {
    if (!isNative) return;

    try {
      await AdMob.initialize({ initializeForTesting: USE_TEST_ADS });

      /* EU/UK consent. Serving personalised ads to an EEA user without this is a
         GDPR problem and Google will stop filling. On a consent form error we
         carry on: AdMob then serves non-personalised ads, which is the safe side. */
      const info = await AdMob.requestConsentInfo();
      if (info?.isConsentFormAvailable && info?.status === 'REQUIRED') {
        await AdMob.showConsentForm();
      }

      ready = true;
    } catch (e) {
      ready = false; // no ads this session; the game is unaffected
    }
  }

  /** Loads and shows one interstitial. Always resolves; never rejects. */
  async function show(reason) {
    if (!isNative || !ready) return false;
    if (Date.now() - lastShown < MIN_GAP_MS) return false;

    const ok = await withTimeout(
      AdMob.prepareInterstitial({ adId: INTERSTITIAL_ID, isTesting: USE_TEST_ADS }),
      LOAD_TIMEOUT_MS,
    );
    if (!ok) return false;

    try {
      await AdMob.showInterstitial(); // resolves once the player dismisses it
      lastShown = Date.now();
      return true;
    } catch (e) {
      return false;
    }
  }

  window.Ads = {
    init,

    /** Before a battle — but never before the player's first one. */
    async beforeGame() {
      const first = gamesPlayed === 0;
      gamesPlayed++;
      if (first) return false;      // let a new player straight into the game
      return show('pre-game');
    },

    /** After a battle ends, before the end screen is read. */
    async afterGame() {
      await idle();                 // let the end screen paint first
      return show('post-game');
    },
  };
})();
