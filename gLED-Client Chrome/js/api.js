"use strict";

// Talks to the gLED controller. Same wire format as the original client:
// POST /data with application/x-www-form-urlencoded fields "type" and "data".
class LEDClient {
    constructor(base = "") {
        this.base = base;
    }

    async _post(type, data) {
        // Raw body like the original client: the firmware's form parser does
        // not percent-decode, so commas and pipes must be sent literally.
        const response = await fetch(this.base + "/data", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: "type=" + type + "&data=" + data,
        });
        const text = await response.text();
        if (!response.ok || text.startsWith("Error")) {
            throw new Error(text.replace(/^Error:\s*/, ""));
        }
        return text;
    }

    // colors: array of [r, g, b] -> "r,g,b|r,g,b|..."
    setPixels(colors) {
        return this._post("set", colors.map((c) => c.join(",")).join("|"));
    }

    // percent: 1 - 100
    setBrightness(percent) {
        return this._post("brightness", String(percent));
    }

    runAnimation(name) {
        return this._post("animation", name);
    }

    stopAnimation() {
        return this._post("animation", "stop");
    }

    // Powers off the controller's OS (GEdge Zero only, advertised via
    // gLED.shutdown). The board needs a power-cycle to come back.
    shutdown() {
        return this._post("shutdown", "now");
    }
}
