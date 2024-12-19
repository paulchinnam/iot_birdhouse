# WORKING VERSION 1

import os
import board
import digitalio
import socketpool
import wifi
import ssl
import binascii
import adafruit_requests
import adafruit_pycamera

# WiFi credentials
WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
SENDGRID_API_KEY = ""

TO_EMAIL = ""       # Replace with recipient email
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

# Initialize camera
print("Initializing camera...")
pycam = adafruit_pycamera.PyCamera()
pycam.display.brightness = 0.0  # Turn off backlight
pycam.resolution = 3            # Set resolution
pycam.autofocus_vcm_step = 145

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

def send_email_with_image(image_data):
    """Send an email with the captured image attached."""
    # Encode the image to Base64 for the email attachment
    encoded_image = binascii.b2a_base64(image_data).strip()

    # Prepare the SendGrid payload
    email_payload = {
        "personalizations": [{"to": [{"email": TO_EMAIL}]}],
        "from": {"email": FROM_EMAIL},
        "subject": "Motion Detected - Image Captured!",
        "content": [{"type": "text/plain", "value": "Motion detected! See the attached image."}],
        "attachments": [
            {
                "content": encoded_image,
                "type": "image/jpeg",
                "filename": "birdfeeder_image.jpg",
                "disposition": "attachment"
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    print("Sending email with image via SendGrid...")
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
        print("Movement detected! Taking picture...")
        # Capture a JPEG image
        jpeg = pycam.capture_into_jpeg()
        if jpeg is not None:
            print("Picture captured! Sending email...")
            send_email_with_image(jpeg)
        else:
            print("ERROR: Failed to capture image!")
    old_pir_value = pir_value# Write your code here :-)
