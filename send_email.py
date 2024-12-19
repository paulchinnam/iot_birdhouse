# SENDING AN EMAIL TEST CODE

import os
import board
import digitalio
import socketpool
import wifi
import ssl
import adafruit_requests

# WiFi credentials
WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
SENDGRID_API_KEY = ""

TO_EMAIL = ""    # Replace with recipient email
FROM_EMAIL = ""  # Replace with your verified sender email

# Connect to WiFi
print("Connecting to WiFi...")
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print("Connected to WiFi!")

# Set up socket pool and SSL context
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

# Initialize PIR sensor
pir = digitalio.DigitalInOut(board.A0)
pir.direction = digitalio.Direction.INPUT

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

def send_email():
    """Send a simple email using SendGrid API."""
    email_payload = {
        "personalizations": [{"to": [{"email": TO_EMAIL}]}],
        "from": {"email": FROM_EMAIL},
        "subject": "Motion Detected!",
        "content": [{"type": "text/plain", "value": "Motion detected by your CircuitPython device!"}]
    }

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    print("Sending email via SendGrid...")
    try:
        response = requests.post(SENDGRID_API_URL, headers=headers, json=email_payload)
        print(f"Email sent! Status code: {response.status_code}")
        if response.status_code >= 400:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"ERROR: Failed to send email! {e}")

print("Waiting for movement...")
old_pir_value = pir.value

while True:
    pir_value = pir.value
    if pir_value and not old_pir_value:
        print("Movement detected! Sending email...")
        send_email()
    old_pir_value = pir_value
