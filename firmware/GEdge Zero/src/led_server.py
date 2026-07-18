# HTTP server and routing, decoupled from the LED hardware.
#
# Serves a single generated HTML page compatible with the gLED
# Chrome/Firefox client: the first configured strip is exposed as the
# global gLED object (same shape as GEdge's, firmware/GEdge/src/led_server.py)
# and also fills the page title/body; additional strips are exposed as
# gLED2, gLED3, gLED4. The "/data" endpoint matches GEdge's, extended with
# a "strip" field so one Pi can address any of its 4 outputs (or all at
# once); each gLED object carries its "strip" value for that field.

import json
import os
import subprocess
import threading

from flask import Flask, request, Response

import config


def _list_animations():
    animations_dir = os.path.join(os.path.dirname(__file__), "..", "animations")
    try:
        files = os.listdir(animations_dir)
    except OSError:
        return []
    return sorted(f[:-3] for f in files if f.endswith(".py") and not f.startswith("__"))


def _strip_gled(strip_name, cfg, animations):
    return {
        "name": cfg.get("name", strip_name),
        "ledCount": cfg["num_pixels"],
        "length": cfg.get("length_cm"),
        "physical": [list(p) for p in cfg.get("physical", [])],
        "animations": animations,
        "strip": strip_name,
        # Board-level capability flag: tells the client to offer a power
        # button (GEdge on the Pico has no OS to shut down, so no flag).
        "shutdown": True,
    }


_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{name}</title>
<script>
{gled_vars}
</script>
</head>
<body>
<h1>{name}</h1>
<p>{count} LEDs, {length} cm</p>
</body>
</html>"""


def _build_index():
    animations = _list_animations()
    strips = list(config.STRIPS.items())
    gled_vars = "\n".join(
        "var gLED{n} = {data};".format(
            n="" if i == 0 else i + 1,
            data=json.dumps(_strip_gled(strip_name, cfg, animations)),
        )
        for i, (strip_name, cfg) in enumerate(strips)
    )
    first_name, first_cfg = strips[0]
    return _PAGE.format(
        name=first_cfg.get("name", first_name),
        gled_vars=gled_vars,
        count=first_cfg["num_pixels"],
        length=first_cfg.get("length_cm"),
    )


def create_server(controllers, runners):
    """Build the Flask app, wiring routes to the given dicts of
    strip name -> StripController / strip name -> AnimationRunner.
    """
    app = Flask(__name__)
    index_page = _build_index()

    @app.route("/", methods=["GET"])
    def get_index():
        return Response(index_page, mimetype="text/html; charset=utf-8")

    @app.route("/favicon.ico", methods=["GET"])
    def get_favicon():
        return Response("")

    @app.route("/data", methods=["POST"])
    def post_data():
        strip_name = request.form.get("strip", "S1")
        data_type = request.form.get("type")
        data = request.form.get("data")
        print("POST /data strip:", strip_name, "type:", data_type)

        if data_type == "shutdown":
            # Graceful poweroff so the SD card is safe to unplug. Delayed so
            # the HTTP response reaches the client first; systemd then stops
            # the service with SIGTERM, which clears the strips (main.py).
            threading.Timer(1.0, subprocess.call, [["poweroff"]]).start()
            return Response("Success!")

        targets = list(controllers.keys()) if strip_name == "all" else [strip_name]
        unknown = [t for t in targets if t not in controllers]
        if unknown:
            return Response("Error:\nUnknown strip(s): " + ", ".join(unknown))

        try:
            for name in targets:
                pixels = controllers[name]
                runner = runners[name]
                if data_type == "set":
                    # Manual pixel data takes over from any running animation.
                    runner.stop()
                    pixels.set_pixels(data)
                elif data_type == "brightness":
                    # Slider sends 1-100; StripController expects 0.0-1.0.
                    pixels.set_brightness(float(data) / 100.0)
                elif data_type == "animation":
                    if data == "stop":
                        runner.stop()
                    else:
                        runner.run_animation(data)
                else:
                    return Response("Error:\nInvalid type")
        except Exception as e:  # pylint: disable=broad-except
            print(e)
            return Response("Error:\n" + str(e))

        return Response("Success!")

    return app
