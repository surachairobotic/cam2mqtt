import base64
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[Info] Connected with result code {rc}", flush=True)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print("[Info] Image received", flush=True)
    try:
        # Decode base64 to bytes
        img_bytes = base64.b64decode(msg.payload)
        # Convert bytes to NumPy array
        np_arr = np.frombuffer(img_bytes, np.uint8)
        # Decode image with OpenCV
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Show image
        cv2.imshow("MQTT Image Viewer", img)
        
        # Wait for 'q' key to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[Info] 'q' key pressed. Exiting...", flush=True)
            cv2.destroyAllWindows()
            client.loop_stop()
            client.disconnect()
            exit(0)
    except Exception as e:
        print("[Info] Error decoding image:", e, flush=True)

# Create MQTT client and connect
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

print(f"[Info] Subscribed to topic: {MQTT_TOPIC}", flush=True)
print("[Info] Waiting for images... Press 'q' in the image window to exit.", flush=True)

try:
    while True:
        pass  # Keep the script running

except KeyboardInterrupt:
    print("\n[Info] Exiting...", flush=True)
    cv2.destroyAllWindows()
    client.loop_stop()
    client.disconnect()
