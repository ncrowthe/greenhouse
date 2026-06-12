# Timelapse camera for Raspbery Pi
# Author: Nigel T. Crowther
# Date: 31-Oct-2025
#
# Set CAMERA_NUMBER to uniquely identify camera image
# For remote maintenance via SSH, see https://phoenixnap.com/kb/enable-ssh-raspberry-pi
#
import json
from time import sleep, time
from picamera2 import Picamera2, Preview
import base64
import requests
from datetime import datetime
from PIL import Image
from PIL import ImageDraw, Image, ImageFont
import socket
import os

CAMERA_NUMBER = 4
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

    print("Hostname: {}, IP: {}".format(hostname, ip))

    return hostname, ip

def initialiseCamera(xPixels, yPixels):
    hostname = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]

    print("Hostname: {}, IP: {}".format(hostname, ip))

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
        
        print("************RESPONSE **********" + response)
    
        jsonData = json.loads(response)
        timelapse_period = jsonData["doc"]["camTimelapse"]
        print("timelapse period: " + str(timelapse_period))

        imageXPixels = jsonData["doc"]["camImageXPixels"]
        print("Image X pixels: " + str(imageXPixels))

        imageYPixels = jsonData["doc"]["camImageYPixels"]
        print("Image height: " + str(imageYPixels))

    except Exception as e:
        if isinstance(e, OSError) and resp: # If the error is an OSError the socket has to be closed.
            print(resp)
            resp.close()
        print("configure(): CONNECTION ERROR.  Using default settings. " + str(e))

    print(f"Timelapse period updated to {timelapse_period} minutes")   
    print(f"Image size updated to {imageXPixels}x{imageYPixels} pixels") 
    
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
        print(f"Wait for internet... ({attempts}/{max_attempts})")
        sleep(1)

    if not checkInternet():
        print("Internet connection not available after {} attempts".format(max_attempts))
        return False

    return True

def generateTimestamp():
    ts = datetime.now().timestamp()
    date_time = datetime.fromtimestamp(ts)
    timestamp = date_time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = str(timestamp)[0:19]
    return timestamp

def postPhoto(image, imageXPixels, imageYPixels, timestamp):

    print("Post photo to server")

    image_64 = base64.b64encode(open(image, "rb").read())

    imageLen = len(image_64)
    print("Image length: {}".format(imageLen))

    # Discard if the image is less than a defined size
    NO_IMAGE = imageXPixels * imageYPixels * 0.05  # Image size below which it is discarded    
    if (imageLen < NO_IMAGE):
        print("Image too dark. Discarding")
        return False

    # Wait until WIFI connected
    if not waitForInternet():
        print("Skipping photo upload due to missing internet connection")
        return False

    # Post photo to server
    url = GREENHOUSE_SERVER_URL + '/photo'
    myobj = {'_id': timestamp, 'cam': CAM_NAME, 'photo': image_64, 'timestamp': timestamp}
    try:
        res = requests.post(url, data=myobj, timeout=30)
        print("POST:" + str(res))
        return True
    except Exception as e:
        print(f'Failed to send photo. {type(e)}: {e}')
        print("Message: {}".format(e))
        return False


def deletePhoto(file):
    # Remove old image if exists
    if os.path.exists(file):
       os.remove(file)
       print("Deleted")

def takePhoto(timestamp, hostname, ip):

    # Start camera and wait
    picam2.start()
    sleep(5)

    # Create image file path
    image = BASE_DIR + str(timestamp) + '.jpg'

    picam2.capture_file(image)

    # specified font size
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf", 32)

    # Open Image
    img = Image.open(image)

    # Call draw Method to embed timestamp into image
    I1 = ImageDraw.Draw(img)

    #Define the coordinates for the rectangle
    xy = [(0, 0), (390, 112)]

    #Draw a filled black rectangle
    I1.rectangle(xy, outline="white", fill="black", width = 4)

    # Add timestamp and hostname to the image
    I1.text((10, 10), timestamp, font=font, fill="white")
    I1.text((10, 36), hostname, font=font, fill="white")
    I1.text((10, 66), ip, font=font, fill="white")

    # Save the edited image
    img.save(image)

    print("Photo taken ")

    return image


##################### Main program #####################

hostname, ip = initialiseInternet()

# Generate timestamp
timestamp = generateTimestamp()
print("Photo" + str(timestamp))

timelapse_period, imageXPixels, imageYPixels = getPhotoSettings()

picam2 = initialiseCamera(imageXPixels, imageYPixels)

print(f"Using settings: {imageXPixels}x{imageYPixels} pixels")

image = takePhoto(timestamp, hostname, ip)

picam2.stop()

status = postPhoto(image, imageXPixels, imageYPixels, timestamp)

if (status == True):
   deletePhoto(image)

print(f"Waiting for next timelapse: {timelapse_period} seconds")
sleep(timelapse_period)