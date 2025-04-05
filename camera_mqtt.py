import cv2
import time
import base64
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import subprocess

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

def is_connected(host="8.8.8.8"):
    try:
        subprocess.check_call(["ping", "-c", "1", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def restart_wifi():
    # Bring the network interface down
    os.system("sudo ifconfig wlan0 down")
    
    # Wait a moment before bringing it back up
    time.sleep(2)
    
    # Bring the network interface up
    os.system("sudo ifconfig wlan0 up")
    
    # Optionally restart the DHCP client to obtain a new IP address
    #os.system("sudo dhclient wlan0")

    # Or restart networking service (this will restart all networking interfaces)
    # os.system("sudo systemctl restart networking")
    time.sleep(5)
    print("Wi-Fi connection restarted")

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

disconnect_count=0
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to capture image.")
            continue

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        if is_connected():
            # Publish to MQTT
            client.publish(MQTT_TOPIC, jpg_as_text)
            print(f"📸 Image published to {MQTT_TOPIC}. disconnect_count={disconnect_count}")
            disconnect_count=0
        else:
            disconnect_count+=1
        if disconnect_count >= 60:
            restart_wifi()

        time.sleep(CAPTURE_INTERVAL)

except KeyboardInterrupt:
    print("🛑 Stopping...")

finally:
    cap.release()
    client.loop_stop()
    client.disconnect()
