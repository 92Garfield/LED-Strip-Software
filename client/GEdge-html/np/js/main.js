let stripArea;

window.addEventListener("load", init);

function init() {
    let grid = document.getElementById("led-grid");
    stripArea = new StripArea(30, 5, 5, grid);

    let brightnessSlider = document.getElementById("brightnessSlider");
    brightnessSlider.addEventListener("change", function () {
        stripArea.brightness = brightnessSlider.value;
    });
}
