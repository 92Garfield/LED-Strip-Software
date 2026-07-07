# gLED Client — Firefox (desktop + Android)

Same extension as `gLED-Client Chrome`; `js/` and `css/` are copies of the
Chrome folder (the source of truth). After changing anything there, run
`./sync.ps1` here. Only `manifest.json` is Firefox-specific
(`browser_specific_settings` with the gecko ID, min version 128 for
`world: "MAIN"` content scripts).

New controller? Add its IP to `matches` AND `host_permissions` in
`manifest.json` (and in the Chrome manifest).

## Try it on desktop (temporary, no signing)

1. Firefox → `about:debugging#/runtime/this-firefox`
2. "Load Temporary Add-on…" → pick this folder's `manifest.json`
3. Visit `http://192.168.2.42/`. Gone after a restart of Firefox.

## Install permanently / on Android (needs Mozilla signing)

Android Firefox only installs signed extensions, so a one-time setup:

1. Zip the contents of this folder (manifest.json at the zip root, not the
   folder itself), e.g. `web-ext build` (`npm i -g web-ext`).
2. Create a (free) account at https://addons.mozilla.org, then
   Developer Hub → "Submit a New Add-on" → choose **"On your own"**
   (unlisted / self-distribution) → upload the zip.
3. After the automatic review you can download the signed `.xpi`.
4. On the phone: open the `.xpi` URL/file in Firefox for Android and confirm
   the install prompt. If nothing happens, put the `.xpi` somewhere
   reachable over http and open that link in Firefox.
5. Grant the site permission if asked (Extensions → gLED Client → Permissions).

Every update needs a version bump in `manifest.json` and a re-upload for
signing. For quick experiments on Android without signing, Firefox Nightly +
a custom add-on collection also works (Settings → About → tap the logo 5x →
Custom Add-on collection).
