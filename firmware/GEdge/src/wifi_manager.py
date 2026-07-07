# WiFi station-mode connection helper.

import ipaddress

import wifi
import socketpool


def connect(ssid, password, static_ip, netmask, gateway, tx_power=15, status=None):
    """Connect to a WiFi network with a static IP and return a SocketPool.

    If a StatusLight is passed, it fast-blinks between connection attempts.
    """
    print("Connecting to WiFi...")

    wifi.radio.set_ipv4_address(
        ipv4=ipaddress.IPv4Address(static_ip),
        netmask=ipaddress.IPv4Address(netmask),
        gateway=ipaddress.IPv4Address(gateway),
    )

    while True:
        # Fast-blink to show "connecting" before each (blocking) attempt.
        if status is not None:
            status.blink_connecting(0.8)
        try:
            wifi.radio.connect(ssid, password)
            break
        except Exception as e:  # pylint: disable=broad-except
            print("WiFi connect failed, retrying:", e)

    wifi.radio.tx_power = tx_power

    print("Connected. IP:", wifi.radio.ipv4_address)
    return socketpool.SocketPool(wifi.radio)
