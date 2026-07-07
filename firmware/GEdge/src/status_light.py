# Debug-by-light status indicator on the onboard LED.
#
# States:
#   off        - just powered up
#   connecting - fast blinking (blocking, driven during the WiFi connect)
#   connected  - steady on
#   pulse      - 5 quick blinks on an incoming request, then back to steady

import time

import board
import digitalio


class StatusLight:
    def __init__(self, pin=board.LED, connecting_interval=0.1,
                 pulse_interval=0.06, pulse_count=5):
        self._led = digitalio.DigitalInOut(pin)
        self._led.direction = digitalio.Direction.OUTPUT
        self._led.value = False

        self._connecting_interval = connecting_interval
        self._pulse_interval = pulse_interval
        self._pulse_count = pulse_count

        self._connected = False
        self._pulse_edges = 0     # remaining on/off edges in the current pulse
        self._next_toggle = 0.0

    # --- steady states -----------------------------------------------------
    def off(self):
        self._connected = False
        self._pulse_edges = 0
        self._led.value = False

    def connected(self):
        self._connected = True
        self._pulse_edges = 0
        self._led.value = True

    # --- connecting: blocking fast blink -----------------------------------
    def blink_connecting(self, duration):
        """Fast-blink for `duration` seconds. Blocking; used while WiFi connects."""
        end = time.monotonic() + duration
        while time.monotonic() < end:
            self._led.value = not self._led.value
            time.sleep(self._connecting_interval)
        self._led.value = False

    # --- request pulse: non-blocking ---------------------------------------
    def request_pulse(self):
        """Queue quick blinks for an incoming request.

        Ignored if a pulse is already running, so a page load that fetches
        several files produces one pulse sequence, not a storm of them.
        """
        if self._pulse_edges > 0:
            return
        self._led.value = False
        self._pulse_edges = self._pulse_count * 2
        self._next_toggle = time.monotonic()

    def update(self):
        """Drive the non-blocking pulse. Call every main-loop iteration."""
        if self._pulse_edges <= 0:
            return
        now = time.monotonic()
        if now >= self._next_toggle:
            self._led.value = not self._led.value
            self._pulse_edges -= 1
            self._next_toggle = now + self._pulse_interval
            if self._pulse_edges <= 0:
                # Pulse finished: restore the steady state.
                self._led.value = self._connected
