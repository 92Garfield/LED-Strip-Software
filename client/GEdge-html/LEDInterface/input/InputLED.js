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