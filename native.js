/* ============================================================
   NATIVE GLUE — Android-only behaviour, no-op in a browser.
   ============================================================ */
(function () {
  'use strict';

  const Cap = window.Capacitor;
  if (!Cap?.isNativePlatform?.()) return;

  const App = Cap.Plugins?.App;
  const ScreenOrientation = Cap.Plugins?.ScreenOrientation;

  // The manifest already pins sensorLandscape; this also covers the case where
  // the user has auto-rotate locked to portrait at the system level.
  ScreenOrientation?.lock({ orientation: 'landscape' }).catch(() => {});

  /* Back button. Default Capacitor behaviour is to close the app, which would
     throw away a battle in progress. Pause instead, and only exit from a screen
     where there is nothing to lose. */
  App?.addListener('backButton', () => {
    const paused = document.getElementById('pausescreen');
    const start = document.getElementById('startscreen');
    const end = document.getElementById('endscreen');

    const onMenu =
      !start?.classList.contains('hidden') || !end?.classList.contains('hidden');

    if (onMenu) {
      App.exitApp();
      return;
    }

    if (paused?.classList.contains('hidden')) {
      document.getElementById('pausebtn')?.click();   // playing -> pause
    } else {
      document.getElementById('resumebtn')?.click();  // paused  -> resume
    }
  });

  /* Losing focus (a call, the home button, an interstitial opening) should never
     leave the game running unattended behind the ad. */
  App?.addListener('appStateChange', ({ isActive }) => {
    if (isActive) return;
    const paused = document.getElementById('pausescreen');
    const start = document.getElementById('startscreen');
    const end = document.getElementById('endscreen');
    const inBattle =
      start?.classList.contains('hidden') &&
      end?.classList.contains('hidden') &&
      paused?.classList.contains('hidden');

    if (inBattle) document.getElementById('pausebtn')?.click();
  });
})();
