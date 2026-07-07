"use strict";

// Physical top view of the strip: the mounting polyline with one dot per LED,
// laid out from gLED.physical (cm coordinates). LED index 0 sits at the first
// polyline point. Tapping or dragging over dots dispatches "ledtap" events.
class StripView extends HTMLElement {
    setup(gled) {
        const { positions, step } = StripView.spread(gled.physical, gled.ledCount);
        this.positions = positions;
        this.dots = [];
        this._render(gled.physical, positions, step);
        this._bindPainting();
        return this;
    }

    // Distribute count points evenly along the polyline, centered per share.
    static spread(points, count) {
        const segments = [];
        let total = 0;
        for (let i = 1; i < points.length; i++) {
            const [x0, y0] = points[i - 1];
            const [x1, y1] = points[i];
            const length = Math.hypot(x1 - x0, y1 - y0);
            segments.push({ x0, y0, x1, y1, start: total, length });
            total += length;
        }
        const step = total / count;
        const positions = [];
        let s = 0;
        for (let i = 0; i < count; i++) {
            const distance = (i + 0.5) * step;
            while (s < segments.length - 1 && distance > segments[s].start + segments[s].length) {
                s++;
            }
            const seg = segments[s];
            const t = (distance - seg.start) / seg.length;
            positions.push([seg.x0 + (seg.x1 - seg.x0) * t, seg.y0 + (seg.y1 - seg.y0) * t]);
        }
        return { positions, total, step };
    }

    _render(points, positions, step) {
        const NS = "http://www.w3.org/2000/svg";
        // gLED.physical is y-up; SVG is y-down, so mirror the y axis.
        points = points.map(([x, y]) => [x, -y]);
        positions = positions.map(([x, y]) => [x, -y]);
        const radius = step * 0.42;
        const pad = radius * 2.5;
        const xs = points.map((p) => p[0]);
        const ys = points.map((p) => p[1]);
        const minX = Math.min(...xs) - pad;
        const minY = Math.min(...ys) - pad;
        const width = Math.max(...xs) - Math.min(...xs) + pad * 2;
        const height = Math.max(...ys) - Math.min(...ys) + pad * 2;

        const svg = document.createElementNS(NS, "svg");
        svg.setAttribute("viewBox", `${minX} ${minY} ${width} ${height}`);

        const line = document.createElementNS(NS, "polyline");
        line.setAttribute("points", points.map((p) => p.join(",")).join(" "));
        line.classList.add("strip-line");
        svg.append(line);

        positions.forEach(([x, y], index) => {
            const dot = document.createElementNS(NS, "circle");
            dot.setAttribute("cx", x);
            dot.setAttribute("cy", y);
            dot.setAttribute("r", radius);
            dot.classList.add("led");
            dot.dataset.index = index;
            svg.append(dot);
            this.dots.push(dot);
        });

        this.append(svg);
    }

    _bindPainting() {
        let painting = false;
        let lastIndex = -1;
        // Paint whatever dot is under the pointer. Going by coordinates
        // instead of event targets makes sliding work on touch, where the
        // browser captures all events to the first-touched element.
        const paintAt = (x, y) => {
            const target = document.elementFromPoint(x, y);
            const index = target && target.dataset ? target.dataset.index : undefined;
            if (index !== undefined && Number(index) !== lastIndex) {
                lastIndex = Number(index);
                this.dispatchEvent(new CustomEvent("ledtap", { detail: { index: lastIndex } }));
            }
        };
        this.addEventListener("pointerdown", (event) => {
            painting = true;
            lastIndex = -1;
            // Undo the implicit capture so moves report elements, not the start dot.
            if (event.target.hasPointerCapture && event.target.hasPointerCapture(event.pointerId)) {
                event.target.releasePointerCapture(event.pointerId);
            }
            paintAt(event.clientX, event.clientY);
            event.preventDefault();
        });
        this.addEventListener("pointermove", (event) => {
            if (painting) paintAt(event.clientX, event.clientY);
        });
        const stop = () => {
            painting = false;
        };
        window.addEventListener("pointerup", stop);
        window.addEventListener("pointercancel", stop);
    }

    setColor(index, rgb) {
        this.dots[index].style.fill = `rgb(${rgb.join(",")})`;
    }

    setColors(colors) {
        colors.forEach((rgb, index) => this.setColor(index, rgb));
    }
}

customElements.define("strip-view", StripView);
