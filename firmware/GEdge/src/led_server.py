# HTTP server and routing, decoupled from the LED hardware.
#
# Serves a single generated HTML page whose inline script exposes the strip
# metadata as a global gLED object (read e.g. by the gLED Chrome extension).

import json
import os
import time

from adafruit_httpserver import Server, Response, POST, GET

import config

_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{name}</title>
<script>
var gLED = {gled};
</script>
</head>
<body>
<h1>{name}</h1>
<p>{count} LEDs, {length} cm</p>
</body>
</html>"""


def _list_animations():
    try:
        files = os.listdir("/animations")
    except OSError:
        return []
    return sorted(f[:-3] for f in files if f.endswith(".py") and not f.startswith("__"))


def _build_index():
    gled = {
        "name": config.LED_NAME,
        "ledCount": config.NUM_PIXELS,
        "length": config.LENGTH_CM,
        "physical": [list(p) for p in config.PHYSICAL],
        "animations": _list_animations(),
    }
    return _PAGE.format(
        name=config.LED_NAME,
        gled=json.dumps(gled),
        count=config.NUM_PIXELS,
        length=config.LENGTH_CM,
    )


def create_server(pool, pixels, runner, status=None, debug=True):
    """Build the HTTP server, wiring routes to the given PixelController
    and AnimationRunner.

    If a StatusLight is passed, each incoming request triggers a blink pulse.
    """
    server = Server(pool, debug=debug)
    index_page = _build_index()

    def _pulse():
        if status is not None:
            status.request_pulse()

    @server.route("/", GET)
    def get_index(request):
        _pulse()
        return Response(request, index_page, content_type="text/html; charset=utf-8")

    @server.route("/favicon.ico", GET)
    def get_favicon(request):
        return Response(request, "")

    @server.route("/data", POST)
    def post_data(request):
        t0 = time.monotonic()
        _pulse()
        t1 = time.monotonic()
        form_data = request.form_data
        data_type = form_data.get("type")
        data = form_data.get("data")
        t2 = time.monotonic()
        print("POST /data type:", data_type)

        try:
            if data_type == "set":
                # Manual pixel data takes over from any running animation.
                runner.stop()
                pixels.set_pixels(data)
            elif data_type == "brightness":
                # Slider sends 1-100; NeoPixel expects 0.0-1.0.
                pixels.set_brightness(float(data) / 100.0)
            elif data_type == "animation":
                if data == "stop":
                    runner.stop()
                else:
                    runner.run_animation(data)
            else:
                return Response(request, "Error:\nInvalid type")
        except Exception as e:  # pylint: disable=broad-except
            print(e)
            return Response(request, "Error:\n" + str(e))
        finally:
            t3 = time.monotonic()
            print(
                "post_data: pulse={:.1f}ms parse_form={:.1f}ms apply={:.1f}ms total={:.1f}ms".format(
                    (t1 - t0) * 1000,
                    (t2 - t1) * 1000,
                    (t3 - t2) * 1000,
                    (t3 - t0) * 1000,
                )
            )

        return Response(request, "Success!")

    return server
