import os
import time
import ipaddress
import wifi
import socketpool
import busio
import board
import microcontroller
import terminalio
import digitalio
from adafruit_httpserver import Server, Request, Response, POST, GET

import neopixel

time.sleep(1)

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

#  onboard LED setup
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# button
button = digitalio.DigitalInOut(board.GP6)
button.switch_to_input(pull=digitalio.Pull.UP)

#create AP unless button is held at start
make_ap = False

if button.value != True:
    make_ap = not make_ap

if make_ap == True:
    print()
    print("Setting up AP")

    # Set access point credentials
    ap_ssid = "YOUR_AP_SSID"
    ap_password = "YOUR_AP_PASSWORD"

    # Configure access point
    wifi.radio.start_ap(ssid=ap_ssid, password=ap_password)
    #wifi.radio.tx_power = int(os.getenv('AP_POWER_TX'))
else:
    #  connect to network
    print("Connecting to WiFi")


    #  set static IP address
    ipv4 =  ipaddress.IPv4Address("192.168.2.42")
    netmask =  ipaddress.IPv4Address("255.255.255.0")
    gateway =  ipaddress.IPv4Address("192.168.2.1")
    wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)
    #  connect to your SSID
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    wifi.radio.tx_power = 15

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)


# @server.route("/", GET)
# def base(request):
#     """
#     Serve a default static plain text message.
#     """
#
#     file = open("./html/index.html", "r")
#
#     #return Response(request, "Hello from the CircuitPython HTTP Server!")
#     return Response(request, file.read(), content_type="text/html")

@server.route("/<path>", GET)
def getRootFile(request, path):
    if (path == "favicon.ico"):
        print("favicon requested")
        return Response(request, "")

    return provideFile(request, f"./html/{path}")

@server.route("/js/<path>", GET)
def getJSFile(request, path):
    return provideFile(request, f"./html/js/{path}")

@server.route("/lib/<path>", GET)
def getLibFile(request, path):
    return provideFile(request, f"./html/lib/{path}")

def provideFile(request, path):
    print(f"path: {path}")
    file = open(path , "r")

    return Response(request, file.read(), content_type="text/html")

# prepare neopixel
pixel_pin = board.GP0
num_pixels = 300
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER)

@server.route("/data", POST)
def postData(request):
    form_data = request.form_data
    print("POST request form data")
    print(f"type: {form_data['type']}")
    print(f"data: {form_data['data']}")

    if form_data['type'] == "set":
        try:
            pixel_data = form_data['data'].split("|")
            pixel_data = [color.split(",") for color in pixel_data]
            pixel_data = [(int(color[0]), int(color[1]), int(color[2])) for color in pixel_data]

            for i in range(len(pixel_data)):
                pixels[i] = (pixel_data[i][0], pixel_data[i][1], pixel_data[i][2])

            pixels.show()
            print(f"pixels: {pixel_data}")
        except Exception as e:
            print(e)
            return Response(request, "Error:\n" + str(e))
    elif form_data['type'] == "brightness":
        try:
            brightness = int(float(form_data['data']))
            pixels.setBrightness(brightness)
            pixels.show()
            print(f"brightness: {brightness}")
        except Exception as e:
            print(e)
            return Response(request, "Error:\n" + str(e))
    else:
        return Response(request, "Error:\nInvalid type")

    return Response(request, "Success!")

# server.serve_forever(str(wifi.radio.ipv4_address_ap))
server.start("192.168.2.42")
iteration_count = 0
clock = time.monotonic()
while True:
    try:
        time.sleep(0.001)
        iteration_count = iteration_count + 1
        if (clock + 5) < time.monotonic():
            clock = time.monotonic()
            #print(f"iteration_count: {iteration_count}")
            #print(f"cpu temp: {microcontroller.cpu.temperature}°C")
            #print(f"time: {time.monotonic()}")

        #  poll the server for incoming/outgoing requests
        server.poll()
    # pylint: disable=broad-except
    except Exception as e:
        # print(e)
        continue