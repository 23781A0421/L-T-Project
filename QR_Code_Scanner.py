import network
import socket
import time
import logging
import picamera
from pyzbar.pyzbar import decode
from PIL import Image
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Wi-Fi Configuration
SSID = "SSID(Change if required)"
PASSWORD = "PASSWORD"

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        logging.info("Connecting to Wi-Fi...")
        time.sleep(1)
    logging.info("Connected to Wi-Fi: %s", wlan.ifconfig())

def start_web_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    logging.info("Web server started on: %s", addr)

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            logging.info("Client connected from: %s", client_address)
            request = client_socket.recv(1024).decode()
            logging.info("Request: %s", request)

            # Capture QR code data
            qr_data = capture_qr_code()

            # Generate HTML response
            response = generate_html(qr_data)
            client_socket.send(response)
        except Exception as e:
            logging.error("Error handling client: %s", str(e))
        finally:
            client_socket.close()

def capture_qr_code():
    try:
        # Initialize the PiCamera
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.start_preview()
            time.sleep(2)
            image_stream = io.BytesIO()
            camera.capture(image_stream, format='jpeg')
            camera.stop_preview()

        # Decode QR code from the captured image
        image_stream.seek(0)
        img = Image.open(image_stream)
        decoded_objects = decode(img)
        qr_data = [obj.data.decode() for obj in decoded_objects]
        logging.info("QR Code data captured: %s", qr_data)
        return qr_data
    except Exception as e:
        logging.error("Failed to capture or decode QR code: %s", str(e))
        return []

def generate_html(qr_data):
    qr_data_display = "<br>".join(qr_data) if qr_data else "No QR code detected!"
    html = f"""
    HTTP/1.1 200 OK
    Content-Type: text/html

    <html>
    <head><title>QR Code Scanner</title></head>
    <body>
        <h1>QR Code Scanner</h1>
        <p>Data: {qr_data_display}</p>
    </body>
    </html>
    """
    return html.encode('utf-8')

if __name__ == "__main__":
    connect_to_wifi()
    start_web_server()