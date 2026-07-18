#!/usr/bin/env python3
# Entry point: HTTP-controlled 4-strip WS2812/NeoPixel driver for a
# Raspberry Pi Zero family board (Zero W / Zero WH / Zero 2 W), wired per
# "PCB/simplified/4-strips, 4-power". Application code lives in /src,
# animations in /animations, shared color helpers in /glib - same layout as
# firmware/GEdge (the Pico W version). See README.md for setup.

import os
import signal
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import config
from strip_controller import StripController
from animation_runner import AnimationRunner
from led_server import create_server

controllers = {}
runners = {}


def _setup_strips():
    for strip_name, cfg in config.STRIPS.items():
        print("Initializing", strip_name, "on GPIO", cfg["gpio"])
        controllers[strip_name] = StripController(
            gpio=cfg["gpio"],
            num_pixels=cfg["num_pixels"],
            channel=cfg.get("channel", 0),
            dma=cfg.get("dma", 10),
        )
        runners[strip_name] = AnimationRunner(controllers[strip_name])

    default_animations = getattr(config, "DEFAULT_ANIMATIONS", {})
    for strip_name, animation_name in default_animations.items():
        if animation_name and strip_name in runners:
            runners[strip_name].run_animation(animation_name)
            print("Running animation:", animation_name, "on", strip_name)


def _animation_loop():
    # Advances every strip's animation; runs alongside the (blocking) Flask
    # server so all strips keep animating while the server handles requests.
    while True:
        for runner in runners.values():
            runner.update()
        time.sleep(0.02)


def _clear_and_exit(signum, frame):
    print("Shutting down, clearing strips...")
    for controller in controllers.values():
        try:
            controller.clear()
        except Exception as e:  # pylint: disable=broad-except
            print(e)
    sys.exit(0)


def main():
    _setup_strips()

    signal.signal(signal.SIGINT, _clear_and_exit)
    signal.signal(signal.SIGTERM, _clear_and_exit)

    threading.Thread(target=_animation_loop, daemon=True).start()

    app = create_server(controllers, runners)
    print("Server starting on {}:{}".format(config.HOST, config.PORT))
    app.run(host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
