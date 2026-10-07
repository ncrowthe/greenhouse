# Timelapse camera for Raspbery Pi
# Author: Nigel T. Crowther
# Date: 31-Oct-2025
#
# Set CAMERA_NUMBER to uniquely identify camera image
# For remote maintenance via SSH, see https://phoenixnap.com/kb/enable-ssh-raspberry-pi
#
import json
import sys
from time import sleep, time
from picamera2 import Picamera2, Preview
import base64
import requests
from datetime import datetime
from PIL import Image
from PIL import ImageDraw, Image, ImageFont
import socket
import os
import logging
from sense_hat import SenseHat

logging.basicConfig(filename="timelapse.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
log = logging.getLogger('picam')
log.setLevel(logging.DEBUG)

CAMERA_NUMBER = 2
#GREENHOUSE_SERVER_URL =  'https://foxhound-hip-initially.ngrok-free.app'
GREENHOUSE_SERVER_URL =  'http://86.4.208.162'
BASE_DIR = '/home/ncrowther/Pictures/greenhouse'
DEVICE_NAME = "zone" + str(CAMERA_NUMBER)
CAM_NAME = "cam" + str(CAMERA_NUMBER)

WAIT_TIME =  60 * 15 # Photo every 15 mins
IMAGE_SIZE = (2592, 1944)

def initialiseInternet():
    hostname = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]

    log.info("Hostname: {}, IP: {}".format(hostname, ip))

    return hostname, ip

def initialiseCamera(xPixels, yPixels):
    hostname = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]

    log.info("Hostname: {}, IP: {}".format(hostname, ip))

    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration(main={"size": (xPixels, yPixels), "format": "RGB888"})
    picam2.configure(camera_config)
    picam2.start_preview(Preview.NULL)

    return picam2

def getPhotoSettings():
    """Get the current timelapse settings from the greenhouse config service."""

    request_url = GREENHOUSE_SERVER_URL + '/config?id=' + DEVICE_NAME
    resp = None
    timelapse_period = WAIT_TIME
    imageXPixels = IMAGE_SIZE[0]
    imageYPixels = IMAGE_SIZE[1]

    response = "ERROR"
    try:
        resp = requests.get(request_url, timeout=30)
        response = resp.text
        resp.close()

        log.info("************RESPONSE **********" + response)

        jsonData = json.loads(response)
        timelapse_period = jsonData["doc"]["camTimelapse"]
        log.info("timelapse period: " + str(timelapse_period))

        imageXPixels = jsonData["doc"]["camImageXPixels"]
        log.info("Image X pixels: " + str(imageXPixels))

        imageYPixels = jsonData["doc"]["camImageYPixels"]
        log.info("Image height: " + str(imageYPixels))

    except Exception as e:
        if isinstance(e, OSError) and resp: # If the error is an OSError the socket has to be closed.
            log.info(resp)
            resp.close()
        log.info("configure(): CONNECTION ERROR.  Using default settings. " + str(e))

    log.info(f"Timelapse period updated to {timelapse_period} minutes")
    log.info(f"Image size updated to {imageXPixels}x{imageYPixels} pixels")

    timelapse_period = timelapse_period * 60 # minutes to seconds
    return timelapse_period, imageXPixels, imageYPixels

    
# Check internet connection
def checkInternet():
    try:
        res = socket.getaddrinfo('google.com',80)
        return True
    except:
        return False

# Function to wait for internet connection
def waitForInternet(max_attempts=10):
    attempts = 0
    while not checkInternet() and attempts < max_attempts:
        attempts += 1
        log.info(f"Wait for internet... ({attempts}/{max_attempts})")
        sleep(1)

    if not checkInternet():
        log.info("Internet connection not available after {} attempts".format(max_attempts))
        return False

    return True

def generateTimestamp():
    ts = datetime.now().timestamp()
    date_time = datetime.fromtimestamp(ts)
    timestamp = date_time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = str(timestamp)[0:19]
    return timestamp

def postPhoto(image, imageXPixels, imageYPixels, timestamp, max_retries=None, retry_delay=60):
    """
    Post photo to server with retry logic until status 200 is returned.

    Args:
        image: Path to the image file
        imageXPixels: Image width in pixels
        imageYPixels: Image height in pixels
        timestamp: Timestamp string
        max_retries: Maximum number of retry attempts (None for infinite retries)
        retry_delay: Delay in seconds between retry attempts (default 60)

    Returns:
        True if photo was successfully posted (status 200), False if image was discarded
    """
    log.info("Post photo to server")

    image_64 = base64.b64encode(open(image, "rb").read())

    imageLen = len(image_64)
    log.info("Image length: {}".format(imageLen))

    # Discard if the image is less than a defined size
    NO_IMAGE = imageXPixels * imageYPixels * 0.05  # Image size below which it is discarded
    if (imageLen < NO_IMAGE):
        log.info("Image too dark. Discarding")
        return False

    # Post photo to server with retry logic
    url = GREENHOUSE_SERVER_URL + '/photo'
    myobj = {'_id': timestamp, 'cam': CAM_NAME, 'photo': image_64, 'timestamp': timestamp}

    attempt = 0
    while True:
        attempt += 1

        # Wait until WIFI connected before each attempt
        if not waitForInternet():
            log.info(f"Attempt {attempt}: No internet connection. Retrying in {retry_delay} seconds...")
            sleep(retry_delay)
            continue

        try:
            res = requests.post(url, data=myobj, timeout=30)
            log.info(f"Attempt {attempt}: POST response - Status: {res.status_code}, Response: {res}")

            if res.status_code == 200:
                log.info("Photo successfully posted with status 200")
                return True
            else:
                log.info(f"Attempt {attempt}: Received status {res.status_code}, retrying in {retry_delay} seconds...")

        except Exception as e:
            log.info(f'Attempt {attempt}: Failed to send photo. {type(e)}: {e}')

        # Check if we've reached max retries
        if max_retries is not None and attempt >= max_retries:
            log.info(f"Max retries ({max_retries}) reached. Giving up on this photo.")
            return False

        # Wait before retrying
        log.info(f"Waiting {retry_delay} seconds before retry...")
        sleep(retry_delay)


def deletePhoto(file):
    # Remove old image if exists
    if os.path.exists(file):
       os.remove(file)
       log.info("Deleted")


def takePhoto(timestamp, hostname, ip, timelapse_period):

    # Start camera and wait
    picam2.start()
    sleep(5)

    # Create image file path
    image = BASE_DIR + str(timestamp) + '.jpg'

    picam2.capture_file(image)

    picam2.stop()

    # specified font size
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf", 32)

    # Open Image
    img = Image.open(image)

    # Call draw Method to embed timestamp into image
    I1 = ImageDraw.Draw(img)

    #Define the coordinates for the rectangle
    xy = [(0, 0), (390, 144)]

    #Draw a filled black rectangle
    I1.rectangle(xy, outline="white", fill="black", width = 4)

    # Add timestamp, hostname, IP and timelapse period to the image
    I1.text((10, 10), timestamp, font=font, fill="white")
    I1.text((10, 36), hostname, font=font, fill="white")
    I1.text((10, 66), ip, font=font, fill="white")
    I1.text((10, 96), f"Period: {timelapse_period // 60} min", font=font, fill="white")

    # Save the edited image

    # Display the image
    #img.show()
    img.save(image)

    log.info("Photo taken ")

    return image


## Draw sensehat image ###############

def smile(sense):

   y = (25, 255, 0) #Yellow
   b = (0, 0, 0) # Black

   smiley_face = [
   y, y, y, y, y, y, y, y,
   y, y, y, y, y, y, y, y,
   y, b, b, y, y, b, b, y,
   y, b, b, y, y, b, b, y,
   y, y, y, y, y, y, y, y,
   y, b, b, y, y, b, b, y,
   y, y, y, b, b, y, y, y,
   y, y, y, y, y, y, y, y
   ]

   sense.set_pixels(smiley_face)

##################### Main program #####################

sense = SenseHat()

hostname, ip = initialiseInternet()

# Get initial photo settings
timelapse_period, imageXPixels, imageYPixels = getPhotoSettings()

# Initialize camera with initial settings
picam2 = initialiseCamera(imageXPixels, imageYPixels)

log.info(f"Using settings: {imageXPixels}x{imageYPixels} pixels")

# Track time for photo capture and settings refresh
last_photo_time = 0
last_settings_check_time = 0
CHECK_INTERVAL = 1 # Check settings every 1 seconds

try:
    while True:
        current_time = time()

        # Check settings (every 1 minute)
        log.info("Checking for updated photo settings...")
        new_timelapse_period, new_imageXPixels, new_imageYPixels = getPhotoSettings()

        # If image size changed, reinitialize camera
        if new_imageXPixels != imageXPixels or new_imageYPixels != imageYPixels:
            log.info(f"Image size changed from {imageXPixels}x{imageYPixels} to {new_imageXPixels}x{new_imageYPixels}")
            picam2.stop()
            picam2.close()
            imageXPixels = new_imageXPixels
            imageYPixels = new_imageYPixels
            picam2 = initialiseCamera(imageXPixels, imageYPixels)

        # Update timelapse period
        if new_timelapse_period != timelapse_period:
            log.info(f"Timelapse period changed from {timelapse_period} to {new_timelapse_period} seconds")
            timelapse_period = new_timelapse_period

        last_settings_check_time = current_time

        elapsed_time = current_time - last_photo_time

        seconds_remaining = int(timelapse_period - elapsed_time)

        if seconds_remaining < 0:
            seconds_remaining = 0

        minutes, secs = divmod(seconds_remaining, 60)
        sense.show_message(f"{minutes}:{secs:02d}")

        # Check if it's time to take a photo
        if seconds_remaining <= 0:
            # Generate timestamp
            timestamp = generateTimestamp()
            log.info("Taking photo: " + str(timestamp))

            smile(sense)

            # Take photo
            image = takePhoto(timestamp, hostname, ip, timelapse_period)

            # Post photo to server
            status = postPhoto(image, imageXPixels, imageYPixels, timestamp, 10, retry_delay=5)

            if status == True:
                deletePhoto(image)

            last_photo_time = current_time

            log.info(f"Next photo in {timelapse_period} seconds")


        # Sleep for a short interval to avoid busy waiting
        sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    log.info("Timelapse stopped by user")
    picam2.stop()
    picam2.close()
    sys.exit(0)
except Exception as e:
    log.error(f"Unexpected error in main loop: {e}")
    picam2.stop()
    picam2.close()
    sys.exit(1)


