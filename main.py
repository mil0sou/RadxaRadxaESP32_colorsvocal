import network
import time
from machine import Pin, I2C
import ssd1306
from umqtt.simple import MQTTClient
import neopixel

NUM_LEDS = 64
PIN = 3
SSID = "milo "
PASS = "niryoned2"
MQTT_BROKER = "192.168.225.167"
CLIENT_ID = "esp32_test_sub"
TOPIC = b"iot_whisper"

np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)

COLORS = {
    "red":       (255, 0, 0),
    "green":     (0, 255, 0),
    "blue":      (0, 0, 255),
    "white":     (255, 255, 255),
    "yellow":    (255, 255, 0),
    "orange":    (255, 128, 0),
    "purple":    (128, 0, 255),
    "pink":      (255, 0, 128),
    "cyan":      (0, 255, 255),
    "magenta":   (255, 0, 255),
    "lime":      (128, 255, 0),
    "teal":      (0, 128, 128),
    "indigo":    (75, 0, 130),
    "violet":    (238, 130, 238),
    "gold":      (255, 215, 0),
    "coral":     (255, 80, 60),
    "salmon":    (255, 100, 80),
    "turquoise": (64, 224, 208),
    "lavender":  (150, 100, 255),
    "mint":      (150, 255, 180),
    "crimson":   (220, 20, 60),
    "scarlet":   (255, 36, 0),
    "maroon":    (128, 0, 0),
    "navy":      (0, 0, 128),
    "sky":       (135, 206, 235),
    "rose":      (255, 50, 100),
    "off":       (0, 0, 0),
    "black": (20, 20, 20),
}

BRIGHTNESS = 0.3
rainbow_mode = False
flash_mode = False
flash_state = False
rainbow_j = 0
last_color = [(0, 0, 0)] * NUM_LEDS

FLAGS = {
    "brazil": [
        # Fond vert
        "green", "green", "green", "green", "green", "green", "green", "green",
        "green", "green", "green", "yellow","yellow","green", "green", "green",
        "green", "green", "yellow","yellow","yellow","yellow","green", "green",
        "green", "yellow","yellow","blue", "blue", "yellow","yellow","green",
        "green", "yellow","yellow","blue", "blue", "yellow","yellow","green",
        "green", "green", "yellow","yellow","yellow","yellow","green", "green",
        "green", "green", "green", "yellow","yellow","green", "green", "green",
        "green", "green", "green", "green", "green", "green", "green", "green",
    ],
    "france": [
        "blue","blue","blue","white","white","white","red","red",
        "blue","blue","blue","white","white","white","red","red",
        "blue","blue","blue","white","white","white","red","red",
        "blue","blue","blue","white","white","white","red","red",
        "blue","blue","blue","white","white","white","red","red",
        "blue","blue","blue","white","white","white","red","red",
        "blue","blue","blue","white","white","white","red","red",
        "blue","blue","blue","white","white","white","red","red",
    ],
    "germany": [
        "black","black","black","black","black","black","black","black",
        "black","black","black","black","black","black","black","black",
        "black","black","black","black","black","black","black","black",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "gold", "gold", "gold", "gold", "gold", "gold", "gold", "gold",
        "gold", "gold", "gold", "gold", "gold", "gold", "gold", "gold",
    ],
    "italy": [
        "green","green","green","white","white","red","red","red",
        "green","green","green","white","white","red","red","red",
        "green","green","green","white","white","red","red","red",
        "green","green","green","white","white","red","red","red",
        "green","green","green","white","white","red","red","red",
        "green","green","green","white","white","red","red","red",
        "green","green","green","white","white","red","red","red",
        "green","green","green","white","white","red","red","red",
    ],
    "spain": [
        "red",    "red",    "red",    "red",    "red",    "red",    "red",    "red",
        "red",    "red",    "red",    "red",    "red",    "red",    "red",    "red",
        "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow",
        "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow",
        "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow",
        "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow",
        "red",    "red",    "red",    "red",    "red",    "red",    "red",    "red",
        "red",    "red",    "red",    "red",    "red",    "red",    "red",    "red",
    ],
    "japan": [
        "white","white","white","white","white","white","white","white",
        "white","white","white","white","white","white","white","white",
        "white","white","red",  "red",  "red",  "white","white","white",
        "white","red",  "red",  "red",  "red",  "red",  "white","white",
        "white","red",  "red",  "red",  "red",  "red",  "white","white",
        "white","white","red",  "red",  "red",  "white","white","white",
        "white","white","white","white","white","white","white","white",
        "white","white","white","white","white","white","white","white",
    ],
    "china": [
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "yellow","red", "yellow","red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        ],
    "korea": [
        "white","white","white","white","white","white","white","white",
        "white","black","white","white","white","black","white","white",
        "white","white","red",  "blue", "red",  "white","white","white",
        "white","white","blue", "red",  "blue", "white","white","white",
        "white","white","red",  "blue", "red",  "white","white","white",
        "white","black","white","white","white","black","white","white",
        "white","white","white","white","white","white","white","white",
        "white","white","white","white","white","white","white","white",
    ],
    "turkey": [
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "white","white","red",  "red",  "yellow","red",  "red",
        "white","red",  "white","white","red",  "red",  "red",  "red",
        "white","red",  "white","white","red",  "yellow","red",  "red",
        "red",  "white","white","red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
    ],
    "mauritius": [
        "red",   "red",   "red",   "red",   "red",   "red",   "red",   "red",
        "red",   "red",   "red",   "red",   "red",   "red",   "red",   "red",
        "blue",  "blue",  "blue",  "blue",  "blue",  "blue",  "blue",  "blue",
        "blue",  "blue",  "blue",  "blue",  "blue",  "blue",  "blue",  "blue",
        "yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow",
        "yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow",
        "green", "green", "green", "green", "green", "green", "green", "green",
        "green", "green", "green", "green", "green", "green", "green", "green",
    ],
    "uk": [
        "blue", "blue", "white","red",  "red",  "white","blue", "blue",
        "blue", "white","white","red",  "red",  "white","white","blue",
        "white","white","red",  "red",  "red",  "red",  "white","white",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "white","white","red",  "red",  "red",  "red",  "white","white",
        "blue", "white","white","red",  "red",  "white","white","blue",
        "blue", "blue", "white","red",  "red",  "white","blue", "blue",
    ],
    "morocco": [
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "green","red",  "red",  "red",  "red",
        "red",  "red",  "green","green","green","red",  "red",  "red",
        "red",  "green","red",  "green","red",  "green","red",  "red",
        "red",  "red",  "red",  "green","red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
        "red",  "red",  "red",  "red",  "red",  "red",  "red",  "red",
    ],
    "scotland": [
        "white","blue", "blue", "blue", "blue", "blue", "blue", "white",
        "blue", "white","blue", "blue", "blue", "blue", "white","blue",
        "blue", "blue", "white","blue", "blue", "white","blue", "blue",
        "blue", "blue", "blue", "white","white","blue", "blue", "blue",
        "blue", "blue", "blue", "white","white","blue", "blue", "blue",
        "blue", "blue", "white","blue", "blue", "white","blue", "blue",
        "blue", "white","blue", "blue", "blue", "blue", "white","blue",
        "white","blue", "blue", "blue", "blue", "blue", "blue", "white",
    ],
}

def draw_flag(flag_name):
    global rainbow_mode, flash_mode, last_color
    rainbow_mode = False
    flash_mode = False
    pattern = FLAGS.get(flag_name)
    if not pattern:
        return False
    for i, color_name in enumerate(pattern):
        r, g, b = COLORS.get(color_name, (0, 0, 0))
        dimmed = (int(r*BRIGHTNESS), int(g*BRIGHTNESS), int(b*BRIGHTNESS))
        np[i] = dimmed
        last_color[i] = dimmed
    np.write()
    return True

def set_color(rgb):
    global last_color
    r, g, b = rgb
    dimmed = (int(r*BRIGHTNESS), int(g*BRIGHTNESS), int(b*BRIGHTNESS))
    for i in range(NUM_LEDS):
        np[i] = dimmed
        last_color[i] = dimmed
    np.write()

def color_wheel(pos):
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def rainbow_step():
    global rainbow_j
    for i in range(NUM_LEDS):
        idx = (i * 256 // NUM_LEDS + rainbow_j) & 255
        np[i] = color_wheel(idx)
    np.write()
    rainbow_j = (rainbow_j + 1) % 255

def flash_step():
    global flash_state
    color = last_color[0] if any(c > 0 for c in last_color[0]) else (80, 80, 80)
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0) if flash_state else color
    np.write()
    flash_state = not flash_state

def oled_init():
    Pin(36, Pin.OUT).value(0); time.sleep_ms(50)
    rst = Pin(21, Pin.OUT); rst.value(0); time.sleep_ms(400); rst.value(1)
    time.sleep_ms(400)
    i2c = I2C(0, scl=18, sda=17)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c, 0x3C)
    oled.fill(0)
    return oled

def message_display(text1, text2, text3, duration):
    oled = oled_init()
    oled.text("Received", 0, 0)
    oled.text(text1, 0, 16)
    oled.text(text2, 0, 32)
    oled.text(text3, 0, 48)
    oled.show()
    if duration != 0:
        time.sleep(duration)
        oled.poweroff()

def wrap(text, width=16):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + (1 if current else 0) <= width:
            current += (" " if current else "") + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def find_colour(msg):
    global rainbow_mode, flash_mode
    msg = msg.decode() if isinstance(msg, bytes) else msg
    lower = msg.lower()

    for flag_name in FLAGS:
        if flag_name in lower:
            draw_flag(flag_name)
            return  

    if "rainbow" in lower:
        rainbow_mode = True
        flash_mode = False
        return

    if "flashing lights" in lower:
        flash_mode = True
        rainbow_mode = False
        return

    rainbow_mode = False
    flash_mode = False

    words = []
    for w in lower.split():
        words.extend(w.split('-'))

    found = []
    for word in words:
        word = ''.join(c for c in word if c.isalpha())
        if word in COLORS and COLORS[word] not in found:
            found.append(COLORS[word])
    if not found:
        return
    segment = NUM_LEDS // len(found)
    for i in range(NUM_LEDS):
        r, g, b = found[i // segment] if i // segment < len(found) else found[-1]
        np[i] = (int(r*BRIGHTNESS), int(g*BRIGHTNESS), int(b*BRIGHTNESS))
        last_color[i] = np[i]
    np.write()

def sub_cb(topic, msg):
    find_colour(msg)
    msg = msg.decode() if isinstance(msg, bytes) else msg
    lines = wrap(msg)
    while len(lines) < 3:
        lines.append("")
    message_display(lines[0], lines[1], lines[2], 3)

def connect_WiFi(ssid, password, timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False); time.sleep_ms(200)
    wlan.active(True);  time.sleep_ms(200)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        t0 = time.time()
        while not wlan.isconnected():
            if time.time() - t0 > timeout:
                raise RuntimeError("WiFi timeout")
            time.sleep(0.2)
    t0 = time.time()
    while wlan.ifconfig()[0] == '0.0.0.0':
        if time.time() - t0 > 5:
            raise RuntimeError("DHCP timeout")
        time.sleep(0.2)
    print("IP:", wlan.ifconfig()[0])
    return True

if connect_WiFi(SSID, PASS):
    print("WiFi connected")
    message_display("connected", "to", SSID, 5)

client = MQTTClient(CLIENT_ID, MQTT_BROKER)
client.set_callback(sub_cb)
client.connect()
print("Connected to broker")
client.subscribe(TOPIC)
print("Subscribed to:", TOPIC)

while True:
    client.check_msg()
    if rainbow_mode:
        rainbow_step()
    elif flash_mode:
        flash_step()
    time.sleep(0.05)
