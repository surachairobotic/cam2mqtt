📸 cam2mqtt ➡️ ☁️
A simple Python application to capture images from a camera and publish them to an MQTT broker. This project also includes a systemd service for running the application in the background on Linux systems.

🛠️ Prerequisites
Ensure the following are installed on your Linux system:

A Linux distribution that uses systemd (e.g., Raspberry Pi OS, Ubuntu, Debian)

git

python3

pip for Python 3

📦 Installation
Clone the repository and install the required Python packages:

bash
Copy
Edit
git clone https://github.com/surachairobotic/cam2mqtt.git
cd cam2mqtt
pip install -r requirements.txt
⚙️ Configuration
Before running the application, update the MQTT and camera settings in camera_mqtt.py:

bash
Copy
Edit
nano camera_mqtt.py
Look for the variables near the top of the file:

MQTT server address

Port

Topic

Username/password

Camera settings (e.g., resolution, interval)

Adjust these values to match your setup.

🧩 Running as a systemd Service
To run cam2mqtt in the background and start it automatically at boot, configure it as a systemd service.

Step 1: Create the Service File
bash
Copy
Edit
sudo nano /etc/systemd/system/cam2mqtt.service
Paste the following content into the file:

⚠️ Important: Replace /home/pi/cam2mqtt with the full absolute path to your cloned project directory.

ini
Copy
Edit
[Unit]
Description=Camera to MQTT Publishing Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/cam2mqtt/camera_mqtt.py
WorkingDirectory=/home/pi/cam2mqtt
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
Save and exit the file (Ctrl+X, then Y, then Enter).

Step 2: Manage the Service
Run the following commands to enable and control the service:

bash
Copy
Edit
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable cam2mqtt.service

# Start the service immediately
sudo systemctl start cam2mqtt.service

# Check the service status
sudo systemctl status cam2mqtt.service
To stop or disable the service:

bash
Copy
Edit
# Stop the service
sudo systemctl stop cam2mqtt.service

# Disable automatic start on boot
sudo systemctl disable cam2mqtt.service
🧰 Troubleshooting
Service Fails to Start
Check the status:

bash
Copy
Edit
sudo systemctl status cam2mqtt.service
Ensure the paths in cam2mqtt.service are correct (pwd can help).

Confirm the specified user has permissions to run the script and access the camera.

No Messages on MQTT Broker
Verify your MQTT settings in camera_mqtt.py.

View real-time logs for errors:

bash
Copy
Edit
sudo journalctl -u cam2mqtt.service -f
📄 License
This project is licensed under the MIT License.

🤝 Contributing
Contributions are welcome! Feel free to submit issues or pull requests.

