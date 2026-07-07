"use strict";

// Tab 1: pick one of the controller's animations, or stop it.
// Dispatches "animation" ({detail: {name}}) and "stopanimation".
class AnimationPanel extends HTMLElement {
    setup(names) {
        this.buttons = new Map();

        const list = document.createElement("div");
        list.classList.add("anim-list");
        for (const name of names) {
            const button = document.createElement("button");
            button.classList.add("anim-button");
            button.textContent = AnimationPanel.pretty(name);
            button.addEventListener("click", () => {
                this.dispatchEvent(new CustomEvent("animation", { detail: { name } }));
            });
            list.append(button);
            this.buttons.set(name, button);
        }

        const stop = document.createElement("button");
        stop.classList.add("stop-button");
        stop.textContent = "Stop animation";
        stop.addEventListener("click", () => this.dispatchEvent(new CustomEvent("stopanimation")));

        this.append(list, stop);
        return this;
    }

    static pretty(name) {
        return name.split("_").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
    }

    setActive(name) {
        for (const [key, button] of this.buttons) {
            button.classList.toggle("active", key === name);
        }
    }
}

customElements.define("animation-panel", AnimationPanel);
