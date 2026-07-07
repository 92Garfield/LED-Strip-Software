class StripArea {
    constructor(columns, rows, spacing, containerElement) {
        this._columns = columns;
        this._rows = rows;
        this._spacing = spacing;
        this._container = containerElement;

        this._entries = [];
        this._coordinates = [];

        this._brightness = 1;
        this._previousDataString = "";
        this._isMouseDown = false;

        this._colorPicker = document.getElementById("colorPicker");

        this._draw();
        this._bindEvents();
    }

    _bindEvents() {
        this._container.addEventListener("mousedown", this._onMouseDown.bind(this));
        this._container.addEventListener("mouseup", this._onMouseUp.bind(this));
        this._container.addEventListener("mousemove", this._onMouseMove.bind(this));

        this._container.addEventListener("touchstart", this._onTouchStart.bind(this), { passive: false });
        this._container.addEventListener("touchend", this._onTouchEnd.bind(this));
        this._container.addEventListener("touchmove", this._onTouchMove.bind(this), { passive: false });
    }

    _onMouseDown(e) {
        this._isMouseDown = true;
        this._paintAtPoint(e.clientX, e.clientY);
    }

    _onMouseUp() {
        this._isMouseDown = false;
    }

    _onMouseMove(e) {
        if (!this._isMouseDown) {
            return;
        }
        this._paintAtPoint(e.clientX, e.clientY);
        this._sendPixelData();
    }

    _onTouchStart(e) {
        e.preventDefault();
        this._isMouseDown = true;
        let touch = e.touches[0];
        this._paintAtPoint(touch.clientX, touch.clientY);
    }

    _onTouchEnd() {
        this._isMouseDown = false;
    }

    _onTouchMove(e) {
        e.preventDefault();
        if (!this._isMouseDown) {
            return;
        }
        let touch = e.touches[0];
        this._paintAtPoint(touch.clientX, touch.clientY);
        this._sendPixelData();
    }

    _paintAtPoint(clientX, clientY) {
        let pickedColor = Number(this._colorPicker.value.replace("#", "0x"));
        this._entries.some((led) => {
            if (led.containsPoint(clientX, clientY)) {
                led.color = pickedColor;
                return true;
            }
            return false;
        });
    }

    _sendPixelData(force) {
        let dataString = this.getDataString();
        if (dataString !== this._previousDataString || force) {
            this._sendData({
                type: "set",
                data: dataString
            });
            this._previousDataString = dataString;
        }
    }

    _sendData(data) {
        console.log("sending", data);
        httpPost("data", data, function (response) {
            console.log(response);
        });
    }

    _generateCoordinates() {
        this._coordinates = [];
        for (let x = 0; x < this._columns; x++) {
            for (let y = 0; y < this._rows; y++) {
                let i;
                if (y % 2 === 0) {
                    i = (y * this._columns) + x;
                } else {
                    i = ((y + 1) * this._columns) - x - 1;
                }
                this._coordinates[i] = { x: x, y: y };
            }
        }
    }

    _draw() {
        this._container.innerHTML = "";
        this._generateCoordinates();
        this._entries = [];

        this._container.style.gridTemplateColumns = "repeat(" + this._columns + ", 1fr)";

        let ledCount = this._columns * this._rows;
        for (let i = 0; i < ledCount; i++) {
            let led = new InputLED();
            this._container.appendChild(led.element);
            this._entries.push(led);
        }
    }

    getLedIndex(x, y) {
        let i;
        if (y % 2 === 0) {
            i = (y * this._columns) + x;
        } else {
            i = ((y + 1) * this._columns) - x - 1;
        }
        return i;
    }

    setColor(x, y, color) {
        let i = this.getLedIndex(x, y);
        this._entries[i].color = color;
    }

    getDataString() {
        let data = [];
        for (let entry of this._entries) {
            let hexStr = entry.color.toString(16).padStart(6, "0");
            let colors = [];
            for (let i = 0; i < 6; i += 2) {
                let colorValue = parseInt(hexStr.substr(i, 2), 16);
                colorValue = Math.round(colorValue * this._brightness);
                colors.push(colorValue);
            }
            data.push(colors.join(","));
        }
        return data.join("|");
    }

    set brightness(value) {
        this._brightness = value / 100;
        this._sendPixelData();
    }

    get brightness() {
        return this._brightness * 100;
    }

    set columns(value) {
        this._columns = value;
        this._draw();
    }

    set rows(value) {
        this._rows = value;
        this._draw();
    }
}
