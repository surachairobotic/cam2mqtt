import base64
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

from datetime import datetime
import time

# Load environment variables
load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# --- Setup for FPS calculation ---
prev_time = time.time()

def img_process(img):
    global prev_time

    # Resize to double the size
    img_resized = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # --- Draw info on image ---
    # Calculate FPS
    current_time = time.time()
    fps = 1.0 / (current_time - prev_time)
    prev_time = current_time

    # Get current time as string
    time_str = datetime.now().strftime('%H:%M:%S')
    fps_str = f'FPS: {fps:.2f}'

    # Combine text lines
    text_lines = [time_str, fps_str]

    # Font and settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    color = (0, 255, 0)  # Green
    margin = 10

    # Put each line at top-right
    for i, line in enumerate(text_lines):
        text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
        x = img_resized.shape[1] - text_size[0] - margin
        y = margin + (i + 1) * (text_size[1] + 5)
        cv2.putText(img_resized, line, (x, y), font, font_scale, color, thickness)

    return img_resized

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

        img_proc = img_process(img)

        # Show image
        cv2.imshow("MQTT Image Viewer", img_proc)
        
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
