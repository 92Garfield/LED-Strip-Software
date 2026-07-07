class InputLED extends PIXI.Container {
    constructor(width, height) {
        super();

        this._width = width;
        this._height = height;

        this._color = 0x000000;

        this._draw();
    }

    _draw() {
        this.removeChildren();

        const background = new PIXI.Graphics();
        background.beginFill(this._color);
        background.drawRect(0, 0, this._width, this._height);
        background.endFill();

        //outline
        background.lineStyle(1, 0xFFFFFF);
        background.drawRect(0, 0, this._width, this._height);

        this.addChild(background);
    }

    set color(color) {
        this._color = color;

        this._draw();
    }

    get color() {
        return this._color;
    }

    set width(width) {
        this._width = width;

        this._draw();
    }

    set height(height) {
        this._height = height;

        this._draw();
    }
}
class StripArea extends PIXI.Container {
    constructor(columns, rows, width, height, spacing) {
        super();

        this._columns = columns;
        this._rows = rows;
        this._width = width;
        this._height = height;
        this._spacing = spacing;

        this._entries = [];
        this._coordinates = [];

        this._brightness = 1;

        this._previousDataString = "";

        this._isMouseDown = false;

        this._colorPicker = document.getElementById("colorPicker");
        console.log(this._colorPicker.value);

        this._draw();

        this.interactive = true;
        this.addEventListener("pointermove", this._touchMove.bind(this));

        this.addEventListener("pointerdown", this._touchDown.bind(this));
        this.addEventListener("pointerup", this._touchUp.bind(this));
    }

    _touchMove(event) {
        // console.log("coords", event.global.x, event.global.y);
        // find LED below pointer
        this._entries.some((led) => {
            if (led.getBounds().contains(event.global.x, event.global.y)) {
                led.color = Number(this._colorPicker.value.replace("#", "0x"));
                return true;
            }
        });

        this._sendPixelData();
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

        httpPost("data", data, function(response) {
            console.log(response);
        });
    }

    _touchDown(event) {
        this._isMouseDown = true;
    }

    _touchUp(event) {
        this._isMouseDown = false;
    }

    _draw() {
        this.removeChildren();
        this._generateCoordinates();

        this._entries = [];

        let entryWidth = (this._width - this._spacing) / this._columns;
        let entryHeight = this._height / this._rows;

        entryWidth = Math.min(entryWidth, entryHeight);
        // noinspection JSSuspiciousNameCombination
        entryHeight = entryWidth;

        let LEDSize = {
            width: entryWidth - this._spacing,
            height: entryHeight - this._spacing
        };

        let ledCount = this._columns * this._rows;
        for (let i = 0; i < ledCount; i++) {
            let coords = this._coordinates[i];
            let x = coords.x * entryWidth + this._spacing;
            let y = coords.y * entryHeight + 50;

            let led = new InputLED(LEDSize.width, LEDSize.height);
            led.x = x;
            led.y = y;

            this.addChild(led);
            this._entries.push(led);
        }

        //debug colors
        // for (let i = 0; i < ledCount; i++) {
        //     let led = this._entries[i];
        //
        //     let red = i * 255 / ledCount;
        //     let green = 255 - red;
        //     let blue = 0;
        //
        //     led.color = (red << 16) + (green << 8) + blue;
        // }
    }

    setColor(x, y, color) {
        let i = this.getLedIndex(x, y);
        this._entries[i].color = color;
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

    set width(value) {
        this._width = value;
        this._draw();
    }

    set height(value) {
        this._height = value;
        this._draw();
    }

    set columns(value) {
        this._columns = value;
        this._draw();
    }

    set rows(value) {
        this._rows = value;
        this._draw();
    }

    _generateCoordinates() {
        for (let x = 0; x < this._columns; x++) {
            for (let y = 0; y < this._rows; y++) {
                let i;
                if (y % 2 === 0) {
                    i = (y * this._columns) + x;
                } else {
                    i = ((y + 1) * this._columns) - x - 1;
                }

                this._coordinates[i] = {
                    x: x,
                    y: y
                };
            }
        }
    }

    getDataString() {
        let data = [];
        for (let entry of this._entries) {
            let hexStr = entry.color.toString(16);
            while (hexStr.length < 6) {
                hexStr = "0" + hexStr;
            }

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
}
