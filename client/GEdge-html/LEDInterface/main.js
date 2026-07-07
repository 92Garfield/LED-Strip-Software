let app, stage;

let stripArea;

window.addEventListener("load", init);
function init() {
    app = new PIXI.Application({
        width          : window.innerWidth,
        height         : 600,
        backgroundColor: 0,
    });

    document.getElementById("pixi").appendChild(app.view);
    app.view.addEventListener("contextmenu", function (e) {
        e.preventDefault();
    });

    stage = app.stage;

    stripArea = new StripArea(30, 5, window.innerWidth, 600, 5);
    stage.addChild(stripArea);

    let brightnessSlider = document.getElementById("brightnessSlider");
    brightnessSlider.addEventListener("change", function() {
        stripArea.brightness = brightnessSlider.value;
    });
}

function sendData(data) {
    console.log("sending", data);

    httpPost("data", data, function(response) {
        console.log(response);
    });
}

window.addEventListener("resize", resize);
function resize() {
    // app.renderer.resize(window.innerWidth, window.innerHeight);
    //
    // stripArea.width = window.innerWidth;
    // stripArea.height = window.innerHeight;
}