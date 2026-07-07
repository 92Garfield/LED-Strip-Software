class InputLED {
    constructor() {
        this._color = 0x000000;

        this.element = document.createElement("div");
        this.element.classList.add("led-cell");

        this._applyColor();
    }

    _applyColor() {
        let hex = this._color.toString(16).padStart(6, "0");
        this.element.style.backgroundColor = "#" + hex;
    }

    getBoundingRect() {
        return this.element.getBoundingClientRect();
    }

    containsPoint(clientX, clientY) {
        let rect = this.getBoundingRect();
        return (
            clientX >= rect.left &&
            clientX <= rect.right &&
            clientY >= rect.top &&
            clientY <= rect.bottom
        );
    }

    set color(color) {
        this._color = color;
        this._applyColor();
    }

    get color() {
        return this._color;
    }
}
