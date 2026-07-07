"use strict";

// Simple tab container: a button bar on top, one visible panel below.
class TabView extends HTMLElement {
    setup() {
        this.buttons = [];
        this.panels = [];
        this.activeIndex = -1;
        this.bar = document.createElement("div");
        this.bar.classList.add("tab-bar");
        this.body = document.createElement("div");
        this.body.classList.add("tab-body");
        this.append(this.bar, this.body);
        return this;
    }

    addTab(label, panel) {
        const index = this.buttons.length;
        const button = document.createElement("button");
        button.classList.add("tab-button");
        button.textContent = label;
        button.addEventListener("click", () => this.select(index));
        this.bar.append(button);
        this.body.append(panel);
        this.buttons.push(button);
        this.panels.push(panel);
        if (index === 0) {
            this.select(0);
        } else {
            panel.classList.add("hidden");
        }
        return this;
    }

    select(index) {
        this.activeIndex = index;
        this.buttons.forEach((button, i) => button.classList.toggle("active", i === index));
        this.panels.forEach((panel, i) => panel.classList.toggle("hidden", i !== index));
    }
}

customElements.define("tab-view", TabView);
