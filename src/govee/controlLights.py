import asyncio
import time
import platform
import subprocess
import os
import tempfile

import json

from govee_led_wez import GoveeController
from govee_led_wez.color import GoveeColor

zones = [
    {"name": 'zone1', "mac": '3C:0F:02:01:53:B2'},
    {"name": 'zone2', "mac": '3C:0F:02:07:7D:BE'},
    {"name": 'zone3', "mac": '3C:0F:02:00:FF:5E'},
    {"name": 'zone4', "mac": '1C:DB:D4:FC:E9:CA'},
]


red = GoveeColor(red=255, green=0, blue=0)
amber = GoveeColor(red=255, green=165, blue=50)
green = GoveeColor(red=0, green=255, blue=0)
blue = GoveeColor(red=0, green=0, blue=255)
white = GoveeColor(red=255, green=200, blue=90)


API_KEY = "e181d76b-3b9c-44df-b69d-e131f5f13367"
#GREENHOUSE_DATASERVICE = 'https://dataservice.27uzmkl2grxv.us-south.codeengine.appdomain.cloud'
GREENHOUSE_DATASERVICE = 'http://86.4.208.162'
ssid = 'VM7763450'
password = 'udWrTpeejf86gugx'

controller = GoveeController()

# Track when each zone was turned on (epoch seconds)
zone_on_timestamps = {}

def record_zone_on(zone):
    """Record the time the zone was turned on."""
    try:
        zone_on_timestamps[zone] = time.time()
        print(f"Recorded {zone} ON at {zone_on_timestamps[zone]}")
    except Exception as e:
        print("record_zone_on error:", e)

def clear_zone_on(zone):
    """Clear the ON timestamp for a zone."""
    if zone in zone_on_timestamps:
        del zone_on_timestamps[zone]
        print(f"Cleared ON timestamp for {zone}")

def color_by_on_duration(onCounter):
    """Return an adjusted GoveeColor based on how long the zone has been ON.
    The longer the zone has been ON, the more red and less green the color becomes.
    """
    try:
        multiplier = 10  # Adjust this multiplier to control how quickly the color changes
        
        if (onCounter < 18):
            greenAdjustment = min(255, int(onCounter * multiplier))  # Increase green by x units per second, max 255
        else:
            greenAdjustment = 0

        redAdjustment = max(0, 255 - greenAdjustment)
        return GoveeColor(red=redAdjustment, green=greenAdjustment, blue=0)

    except Exception as e:
        print("color_by_on_duration error:", e)
        return GoveeColor(red=255, green=0, blue=0)  # Default to red on error


async def update_zone_color_bassed_on_time_in_state(zone, onCounter):
    """Adjust zone1 color based on current state and update the BLE device."""

    print (f"{zone} has been ON for {onCounter} seconds")

    state = getState(zone.get('name'))
    if state == "ON":
        onCounter = min(onCounter + 1, 60)

    elif state == "OFF":
        onCounter = max(onCounter - 1, 0)

    else:  # AUTO
        return onCounter

    adjusted = color_by_on_duration(onCounter)

    await controller.set_color(zone.get('mac'), adjusted)    

    #await controller.set_color(zone.get('mac'), white)    

    await asyncio.sleep(1)  # Wait for 1 second before allowing another update to avoid overwhelming the device
    
    return onCounter

async def update_zone_color_based_on_state(zone):
    """Adjust zone1 color based on current state and update the BLE device."""

    state = "OFF" #getState(zone.get('name'))

    print (f"Zone: {zone} State: {state}")     
    
    if state == "ON":
        color = green
    elif state == "OFF":
        color = white # red
    else:
        color = amber

    await controller.set_color(zone.get('mac'), color)    


    await asyncio.sleep(1)  # Wait for 1 second before allowing another update to avoid overwhelming the device
    
    return


def connect_to_wifi(ssid=ssid, password=password):
    """Connect to a Wi-Fi network using the configured SSID and password."""
    system = platform.system()
    print(f"Connecting to Wi-Fi network '{ssid}' on {system}...")

    if system == "Linux":
        try:
            subprocess.run(
                ["nmcli", "device", "wifi", "connect", ssid, "password", password],
                check=True,
            )
            print(f"Connected to {ssid}")
        except FileNotFoundError:
            print("nmcli not found. Install NetworkManager or use another Wi-Fi tool.")
        except subprocess.CalledProcessError as exc:
            print("Wi-Fi connection failed:", exc)

    elif system == "Windows":
        profile_xml = f"""<?xml version=\"1.0\"?>
<WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
                f.write(profile_xml)
                profile_path = f.name

            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}"], check=True)
            subprocess.run(["netsh", "wlan", "connect", ssid], check=True)
            os.remove(profile_path)
            print(f"Connected to {ssid}")
        except Exception as exc:
            print("Windows Wi-Fi connection failed:", exc)

    else:
        print(f"Unsupported OS for automatic Wi-Fi connection: {system}")


def getState(zoneName):

    print(f"Getting state for {zoneName} from data service...")
    
    color = amber

    request_url = GREENHOUSE_DATASERVICE + '/config?id=' + zoneName
    timeout_seconds = 10

    try:
        with urllib.request.urlopen(request_url, None, timeout_seconds) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except Exception as exc:
        print(f"HTTP request failed for {request_url}: {exc}")
        return None

    print(f"Received payload for {zoneName}: {payload}")

    doc = payload.get('doc', {})
    pump_state = doc.get('pumpState', '')
    print(f"Pump state for {zoneName}: {pump_state}")
  
    return pump_state


def device_changed(device):
    print(f"{device} state changed ")  


async def run_async_tasks():

    controller.set_device_change_callback(device_changed)

    connect_to_wifi(ssid=ssid, password=password)

    # Wait for WIFI connection to establish 
    await asyncio.sleep(1)

    # This will look for devices. It needs to perform discovery and can
    # take several seconds
    result = await controller.query_ble_devices()

    print(f"Queried BLE devices, found {len(result)} devices")
    print("Devices: ")
    for device in result:
        print(f" - {device}")
        
    while True:  
        try:
            for zone in reversed(zones):
                print(f"Controlling {zone['name']} light over BLE")
                await update_zone_color_based_on_state(zone)

        except Exception as e:
            print("Error in main loop:", e)
            #raise


def main():

    connect_to_wifi()
    try:
        
        asyncio.run(run_async_tasks())
        time.sleep(100000)
    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    main()