# Мечкин Камен — 1903

A historical first-person wave-defence game about the **Battle of Mechkin Kamen,
12 August 1903**, during the Ilinden Uprising. The player is a komita defending
the rocks above Kruševo — the Kruševo Republic — against Bahtiyar Pasha's askers.
Survive ten waves. The voivode Pitu Guli's line, "Овде ќе се умре!", is the
game's spine.

**The UI and all copy are in Macedonian.** Keep it that way unless explicitly
asked; the language is part of the subject, not an accident.

The art direction is deliberately **Minecraft-like** — voxel geometry, 16×16
nearest-filtered procedural textures, a hand-rolled bloom pass standing in for a
shader pack. This is finished and intentional. Do not "improve" it into realism.

---

## Layout

```
mechkin-kamen.html   THE GAME — a single ~3,200-line file. Everything lives here:
                     renderer, terrain, enemies, weapons, HUD, audio, leaderboard.
vendor/three.min.js  Three.js r128, bundled (see "Do not break" below)
ads.js               AdMob layer. Currently a no-op. See its header comment.
native.js            Capacitor glue: back button, orientation, auto-pause
privacy.html         Play-required privacy policy, served from GitHub Pages
scripts/
  build-www.mjs      Stages www/ for Capacitor
  make-icons.py      Regenerates every launcher icon + Play store assets
android/             Capacitor Android project (committed)
play/                Play Console assets + LISTING.md (paste-ready copy)
```

The game is a single HTML file on purpose. It is also deployed as-is to GitHub
Pages, so it must keep working when opened directly in a browser.

## Build

```bash
npm run build            # stage www/
npx cap sync android     # push www/ + plugins into the Android project
cd android && ./gradlew assembleDebug     # debug APK
cd android && ./gradlew bundleRelease     # signed .aab for Play
```

Requires `JAVA_HOME` (Temurin 21) and `ANDROID_HOME`
(`/opt/homebrew/share/android-commandlinetools`). Both are exported in `~/.zshrc`.

Install on a connected phone:
`adb install -r android/app/build/outputs/apk/debug/app-debug.apk`

---

## Do not break these

Each of these cost real debugging time. They look like cruft. They are not.

**Three.js is bundled, never from a CDN.** It used to load from cdnjs, which
means the packaged Android app and any offline player got a black screen. If you
upgrade it, upgrade the file in `vendor/`. Note r128 → r18x is a breaking jump
(lighting intensities and colour management both changed); it buys nothing for
shipping, so it has not been done.

**`CAMERA_FAR` (600) is not a performance knob.** The sky dome is a sphere of
radius 480 and the sun sits ~360 out. Lowering the far plane clips the sky away
and leaves the black clear-colour showing through as a giant dome. Fog, not the
far plane, is what limits visible terrain.

**`captureInput` must stay `false`** in `capacitor.config.json`. It is meant for
hardware-keyboard capture and it swallows the touch stream that drag-to-aim needs.

**The Capacitor config is `.json`, not `.ts`.** This project has no TypeScript,
and the Capacitor CLI's `.ts` config parser breaks on TypeScript 6.

**The AdMob SDK is deliberately not installed.** Merely linking it makes Android
request `ACCESS_ADSERVICES_AD_ID` / `_ATTRIBUTION` / `_TOPICS`, which obliges a
Play Data-safety declaration that the app collects an advertising identifier —
untrue while ads are off. `ads.js` degrades to a no-op without it. Its header
comment has the exact steps to turn ads back on.

**Every Play upload needs a higher `versionCode`.** Currently `1`, in
`android/app/build.gradle`. Play will never let a number be reused.

**Secrets:** `upload-keystore.jks` and `android/keystore.properties` are
gitignored and must stay that way. The `.gitignore` globs are deliberately loose
(`*.jks*`) because a keystore renamed to `.jks.old` once nearly got committed.

---

## Performance

There is a `Q` quality tier near the top of the game script. It detects a phone
and cuts pixel ratio to 1.25, the shadow map to 1024/PCF, and the bloom chain to
one pass at 35% scale. Desktop keeps the full settings.

Separately, the game has its own runtime `perfSample()` that sheds bloom, then
resolution, if the average frame exceeds 40ms. The two systems cooperate.

Measured **76 fps on a Samsung Galaxy A36** (mid-range Mali GPU). There is
headroom, but raising the pixel ratio to 1.5 costs 1.44× the fragments (~19ms)
and would drop it under 60. Not worth it.

---

## Where this stands

The app **builds, is signed, and runs**. It has not been submitted yet.

Done: offline assets, mobile quality tier, landscape HUD, Capacitor Android
project, launcher icon, store assets, privacy policy (live on Pages), release
`.aab` (2.9 MB, `INTERNET` permission only).

Next: see `play/LISTING.md`. The blocker is a Play developer account — and note
that **personal** accounts created after Nov 2023 must run a closed test with 12
testers for 14 continuous days before applying for production. Organization
accounts are exempt (the signing cert already says `O=TEMIL`), but the account
type cannot be changed after registration.

**Verified on hardware (Samsung, `RZCTA18857A`, 2026-07-15):** drag-to-aim,
firing, weapon switching, landscape HUD, and auto-pause all work with
`captureInput` off. This was the last shipping blocker.
