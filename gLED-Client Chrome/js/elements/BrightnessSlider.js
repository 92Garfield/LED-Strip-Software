"use strict";

// Strip-global brightness (1-100%). Updates its label while dragging and
// dispatches "brightness" ({detail: {percent}}) when the slider is released.
class BrightnessSlider extends HTMLElement {
    setup(percent = 100) {
        this.title = "Brightness";

        const icon = document.createElement("span");
        icon.classList.add("icon");
        icon.textContent = "☀";

        this.slider = document.createElement("input");
        this.slider.type = "range";
        this.slider.min = "1";
        this.slider.max = "100";
        this.slider.addEventListener("input", () => this._showValue());
        this.slider.addEventListener("change", () => {
            this.dispatchEvent(new CustomEvent("brightness", { detail: { percent: this.percent } }));
        });

        this.label = document.createElement("span");
        this.label.classList.add("value");

        this.append(icon, this.slider, this.label);
        this.percent = percent;
        return this;
    }

    get percent() {
        return Number(this.slider.value);
    }

    set percent(value) {
        this.slider.value = value;
        this._showValue();
    }

    _showValue() {
        this.label.textContent = this.slider.value + "%";
    }
}

customElements.define("brightness-slider", BrightnessSlider);
