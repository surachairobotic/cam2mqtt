import cv2
import time
import base64
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", 5))

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected successfully")
    else:
        print(f"Connection failed with reason code {reason_code}")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"Disconnected with reason code {reason_code}")

# Initialize MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

# Open the USB camera (default /dev/video0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Could not open camera.")
    exit()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to capture image.")
            continue

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # Publish to MQTT
        client.publish(MQTT_TOPIC, jpg_as_text)
        print(f"📸 Image published to {MQTT_TOPIC}")

        time.sleep(CAPTURE_INTERVAL)

except KeyboardInterrupt:
    print("🛑 Stopping...")

finally:
    cap.release()
    client.loop_stop()
    client.disconnect()
