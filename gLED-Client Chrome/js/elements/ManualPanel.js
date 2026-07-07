"use strict";

// Tab 2: manual color setting. Pick a color, tap LEDs in the strip view to
// paint them, set the whole strip, and choose between auto-update on every
// tap or an explicit send. Dispatches "setall" and "send".
class ManualPanel extends HTMLElement {
    setup() {
        this.picker = document.createElement("input");
        this.picker.type = "color";
        this.picker.value = "#ff4000";

        const pickerLabel = document.createElement("label");
        pickerLabel.classList.add("color-label");
        pickerLabel.append(this.picker, document.createTextNode("Color"));

        const setAll = document.createElement("button");
        setAll.textContent = "Set all";
        setAll.addEventListener("click", () => this.dispatchEvent(new CustomEvent("setall")));

        this.autoBox = document.createElement("input");
        this.autoBox.type = "checkbox";
        const autoLabel = document.createElement("label");
        autoLabel.classList.add("auto-label");
        autoLabel.append(this.autoBox, document.createTextNode("Auto update"));
        this.autoBox.addEventListener("change", () => this._updateSendButton());

        this.sendButton = document.createElement("button");
        this.sendButton.classList.add("send-button");
        this.sendButton.textContent = "Send";
        this.sendButton.addEventListener("click", () => this.dispatchEvent(new CustomEvent("send")));

        this.append(pickerLabel, setAll, autoLabel, this.sendButton);
        return this;
    }

    _updateSendButton() {
        this.sendButton.disabled = this.autoUpdate;
    }

    // Selected color as [r, g, b]
    get color() {
        const hex = this.picker.value;
        return [1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16));
    }

    get autoUpdate() {
        return this.autoBox.checked;
    }

    // Mark unsent local changes on the send button.
    setDirty(dirty) {
        this.sendButton.classList.toggle("dirty", dirty);
    }
}

customElements.define("manual-panel", ManualPanel);
