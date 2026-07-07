# gLED — WLAN LED Strip

NeoPixel strip on a Raspberry Pi Pico W (CircuitPython 9), controlled via browser extension.

## Folders

- `firmware/GEdge` — CIRCUITPY drive content (kitchen strip, 150 LEDs, `192.168.2.42`)
- `gLED-Client Chrome` — Chrome extension, **source of truth** for client `js/` + `css/`
- `gLED-Client Firefox` — Firefox extension (desktop + Android), only `manifest.json` differs
- `client/GEdge-html` — old on-controller web client (retired, kept for reference)

## Firmware (`firmware/GEdge`)

- Copy `src/config.example.py` to `src/config.py`, then set WiFi, IP, LED count, name, physical layout, and default animation
- `src/led_server.py` — HTTP server; serves one tiny HTML page exposing global `gLED`
- `src/animation_runner.py` — non-blocking animation loop beside the server
- `animations/*.py` — one class `Animation` per file (`start(now)` / `step(now)`)
  - `hue_cycle` — whole strip, hue rotates (interval + step configurable)
  - `fill_runner` — red runner right→left stacks until full, then back to blue
- `glib/color.py` — `hsv_to_rgb()` for NeoPixel
- Boot: connects WiFi, starts server, autostarts `config.DEFAULT_ANIMATION`

## HTTP API (`POST /data`, urlencoded, values NOT percent-encoded)

- `type=set` `data=r,g,b|r,g,b|…` — set all pixels (stops animation)
- `type=brightness` `data=1..100`
- `type=animation` `data=<name>` or `data=stop`
- `GET /` — HTML with `var gLED = {name, ledCount, length, physical, animations}`

## Clients (extensions)

- Run on the controller page, replace it entirely with their own UI
- Custom elements (`js/elements/`), built by `js/app.js`, dark CSS
- Show physical layout (y-up), tabs: Animation / Manual (tap LEDs to paint)
- No live data from server; last set state kept in `localStorage`
- Brightness slider in header

### Chrome

- `chrome://extensions` → Developer mode → Load unpacked → `gLED-Client Chrome`

### Firefox (desktop + Android)

- After client changes: run `gLED-Client Firefox/sync.ps1` (copies `js/`+`css/` from Chrome)
- Desktop test: `about:debugging` → Load Temporary Add-on
- Android: needs signed `.xpi` via addons.mozilla.org (unlisted) — see `gLED-Client Firefox/README.md`

## New controller / IP change

Update the IP in **3 places**:

- `gLED-Client Chrome/manifest.json` → `matches`
- `gLED-Client Firefox/manifest.json` → `matches` **and** `host_permissions`
- Firmware: `src/config.py` → `STATIC_IP`
