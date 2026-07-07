"use strict";

// Entry point: takes over the controller's page. Reads the global gLED object
// from the served HTML, wipes the body and rebuilds the whole UI from it.
// No data comes from the server besides that HTML: the strip view only shows
// the last state this client has set (persisted in localStorage per strip).
(function () {
    const gled = window.gLED;
    if (!gled || !customElements.get("strip-view")) return;

    const client = new LEDClient();
    const storageKey = "gled-client:" + gled.name;

    // --- last-set state -----------------------------------------------------
    function loadState() {
        try {
            const state = JSON.parse(localStorage.getItem(storageKey));
            if (state && Array.isArray(state.colors) && state.colors.length === gled.ledCount) {
                if (typeof state.brightness !== "number") state.brightness = 100;
                return state;
            }
        } catch (e) { /* fall through to default */ }
        return {
            colors: Array.from({ length: gled.ledCount }, () => [0, 0, 0]),
            animation: null,
            brightness: 100,
        };
    }
    function saveState() {
        try {
            localStorage.setItem(storageKey, JSON.stringify(state));
        } catch (e) { /* storage unavailable: state is session-only */ }
    }
    const state = loadState();
    let dirty = false;

    // --- page skeleton -------------------------------------------------------
    // The controller page ships no viewport meta; without one, phones render
    // the desktop layout zoomed out.
    if (!document.querySelector("meta[name=viewport]")) {
        const viewport = document.createElement("meta");
        viewport.name = "viewport";
        viewport.content = "width=device-width, initial-scale=1";
        document.head.append(viewport);
    }
    document.title = gled.name;
    document.body.innerHTML = "";
    document.body.classList.add("gled");

    const header = document.createElement("header");
    const title = document.createElement("h1");
    title.textContent = gled.name;
    const meta = document.createElement("span");
    meta.classList.add("meta");
    meta.textContent = `${gled.ledCount} LEDs · ${gled.length} cm`;
    const status = document.createElement("span");
    status.classList.add("status");
    const brightness = document.createElement("brightness-slider").setup(state.brightness);
    header.append(title, meta, brightness, status);

    const strip = document.createElement("strip-view").setup(gled);
    strip.setColors(state.colors);

    const animations = document.createElement("animation-panel")
        .setup(gled.animations || []);
    animations.setActive(state.animation);

    const manual = document.createElement("manual-panel").setup();

    const tabs = document.createElement("tab-view").setup()
        .addTab("Animation", animations)
        .addTab("Manual", manual);

    document.body.append(header, strip, tabs);

    // --- server communication ------------------------------------------------
    function report(promise, okText) {
        status.textContent = "Sending…";
        status.className = "status busy";
        return promise
            .then(() => {
                status.textContent = okText;
                status.className = "status ok";
                saveState();
            })
            .catch((error) => {
                status.textContent = "Failed: " + error.message;
                status.className = "status error";
            });
    }

    function sendPixels() {
        dirty = false;
        manual.setDirty(false);
        state.animation = null;
        animations.setActive(null);
        return report(client.setPixels(state.colors), "Colors sent");
    }

    // Sliding over LEDs paints many in quick succession; debounce the
    // auto-update so a stroke becomes one request, not one per LED.
    let autoSendTimer = null;
    function scheduleSend() {
        clearTimeout(autoSendTimer);
        autoSendTimer = setTimeout(sendPixels, 200);
    }

    function paint(index, color) {
        state.colors[index] = color;
        strip.setColor(index, color);
        if (manual.autoUpdate) {
            scheduleSend();
        } else {
            dirty = true;
            manual.setDirty(true);
        }
    }

    // --- wiring ---------------------------------------------------------------
    strip.addEventListener("ledtap", (event) => {
        // Painting only makes sense while the manual tab is open.
        if (tabs.panels[tabs.activeIndex] === manual) {
            paint(event.detail.index, manual.color);
        }
    });

    manual.addEventListener("setall", () => {
        const color = manual.color;
        state.colors = state.colors.map(() => color);
        strip.setColors(state.colors);
        if (manual.autoUpdate) {
            sendPixels();
        } else {
            dirty = true;
            manual.setDirty(true);
        }
    });

    manual.addEventListener("send", () => {
        sendPixels();
    });

    animations.addEventListener("animation", (event) => {
        const name = event.detail.name;
        state.animation = name;
        animations.setActive(name);
        report(client.runAnimation(name), "Animation: " + AnimationPanel.pretty(name));
    });

    brightness.addEventListener("brightness", (event) => {
        state.brightness = event.detail.percent;
        report(client.setBrightness(state.brightness), `Brightness ${state.brightness}%`);
    });

    animations.addEventListener("stopanimation", () => {
        state.animation = null;
        animations.setActive(null);
        report(client.stopAnimation(), "Animation stopped");
    });
})();
