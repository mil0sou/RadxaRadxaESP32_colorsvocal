#!/usr/bin/env python3

import socket
import subprocess
import tempfile
import os
from paho.mqtt import client as mqtt_client

# =========================
# CONFIG
# =========================

UDP_IP = "0.0.0.0"
UDP_PORT = 9999

MQTT_BROKER = "192.168.225.167"
MQTT_PORT = 1883
MQTT_TOPIC = "iot_whisper"

PIPER_MODEL = "models/female.onnx"

# =========================
# MQTT
# =========================

client = mqtt_client.Client(
    callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2
)

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

# =========================
# UDP SERVER
# =========================

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"🎧 UDP listening on {UDP_PORT}")
print(f"📡 MQTT -> {MQTT_BROKER}:{MQTT_PORT} ({MQTT_TOPIC})")
print(f"🔊 Piper model -> {PIPER_MODEL}")
print("-" * 60)

while True:
    data, addr = sock.recvfrom(4096)

    text = data.decode("utf-8").strip()

    if not text:
        continue

    print(f"[UDP] {addr[0]} -> {text}")

    # =========================
    # MQTT SEND
    # =========================

    client.publish(MQTT_TOPIC, text)

    print("[MQTT] sent")

    # =========================
    # PIPER TTS
    # =========================

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name

        # Generate speech
        p1 = subprocess.Popen(
            [
                "piper",
                "--model",
                PIPER_MODEL,
                "--output_file",
                wav_path
            ],
            stdin=subprocess.PIPE,
            text=True
        )

        p1.communicate(text)

        # Play audio
        subprocess.run(
            ["aplay", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        os.remove(wav_path)

    except Exception as e:
        print("TTS error:", e)

