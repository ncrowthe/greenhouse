import sys
import math
from machine import Pin, PWM, ADC, I2C
import time
import binascii
import machine
import asyncio
import random
from StatusLight import StatusLight
from Errors import HardwareError


#################################################
### Greenhouse controller for Rasberry Pi Pico ###
### Author: Nigel T. Crowther
### Date: 03-Sep-2024
#################################################

class OnOffState():
    ON = "ON"
    OFF = "OFF"
    AUTO = "AUTO"  
    
class WindowState():
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    AUTO = "AUTO"
        
# Abtract class for controller devices

    """
    This class is a controller for an ON/OFF device.
    
    Attributes:
        state (OnOffState): The current state of the device.
    
    Methods:
        setState(state): Sets the state of the device.
        status(): Returns the current state of the device.
    """
class OnOffController:
    
    state = OnOffState.AUTO
        
    def setState(self, state):
        
        if not hasattr(OnOffState, state) : 
            print('**Invalid state:' + str(state))
            return
        
        #print('**Set state:' + str(self.state) + "->" + str(state))
        
        if (state == OnOffState.ON):
            self.on()
        elif (state == OnOffState.OFF):
            self.off()
        #elif (state == OnOffState.AUTO):
            # Do nothing               
   
        self.state = state                    
            
    def status(self):
        return self.state
                        
"""
The Light class has methods to turn the light on and off, as well as to control the light based on a given time.
"""
class LightSwitch(OnOffController):
    # Relay light switch

    def __init__(self, pinNumber):
        # GPIO pin number  relay is connected to
        RELAY_PIN = pinNumber
        self.relay_pin = Pin(RELAY_PIN, Pin.OUT)
        self.state = OnOffState.OFF                 
            
    def on(self):
        self.relay_pin.value(1)  # Set relay to ON state
            
    def off(self):   
        self.relay_pin.value(0)  # Set relay to OFF state
        
    def control(self, rtc):
        print("Light state %s" %self.status())
                 


"""
The Pump class has methods for controlling the pump's speed, turning it off, and watering the plants. 
It also has a control method that determines when to water the plants based on temperature and time.
"""
class Pump(OnOffController):
    
    #### DEFINE WATERING TIMES HERE ####
    WATERING_TIMES = [6, 12, 18]
    WATERING_DURATION = 1 # minutes

    def __init__(self, pinNumber):
        # GPIO pin number  relay is connected to
        RELAY_PIN = pinNumber
        self.relay_pin = Pin(RELAY_PIN, Pin.OUT)
        
    def on(self):
        #print("Pump ON")
        self.relay_pin.value(1)  # Set relay to ON state
            
    def off(self):   
        #print("Pump OFF")
        self.relay_pin.value(0)  # Set relay to OFF state
              
    def control(self):    
        print("Pump state %s" %self.status())
     
    def setTimes(self, wateringTimes, period, minTemp):
        self.WATERING_TIMES = wateringTimes
        self.WATERING_DURATION = period      
        
"""
This code controls various devices such as a pump, fan, heater, , and probe. 
The "careforplants" method performs various tasks such as controlling the lights, temperature, watering, and displaying data on the Oled screen. 
It also includes error handling to handle hardware errors and general exceptions.
"""
class PlantCare(object):
    
    # define temperature range
    MIN_TEMPERATURE  = 15
    MAX_TEMPERATURE = 25
        
    def __init__(self, ip, zoneName, pumpPin, lightPin):
        
        try:
            self.ip = ip
            self.zoneName = zoneName
            
            self.pump = Pump(pumpPin)
            self.light = LightSwitch(lightPin)

            # Startup check
            self.pump.setState(OnOffState.OFF)
            self.light.setState(OnOffState.OFF)            
            
        except HardwareError as e:
            print("Exception: " + str(e))
            
            statusLight = StatusLight()
            statusLight.setErroredStatus()                 
        
    def setDateTime(self, datetime):
        return        
             
    def setHeater(self, state):  
        return
          
    def setWindow(self, state):      
        return
        
    def setWindowRun(self, runSecs):      
        return
        
    def setWindowPause(self, pauseSecs):      
        return      
        
    def setLight(self, state):
        self.light.setState(state)              
        return
        
    def setLightOnOffTime(self, onTime, offTime):
        return       
        
    def setTemperatureRange(self, min, max):      
        print("Set temp range: {}-{}".format(min, max))     
        self.MIN_TEMPERATURE = min
        self.MAX_TEMPERATURE = max
        
    def getTemperatureData(self):
        return random.randint(20, 25)
    
    def getHumidityData(self):
        return random.randint(50, 55)      
    
    def setPump(self, state):
        self.pump.setState(state)
        
    def setFan(self, state):
        return      
           
    def setWateringTimes(self, wateringTimes, period, minTemp):
        
        if (period == None):
            period = 1 # Minutes
            
        if (minTemp == None):
            minTemp = 10 # C
            
        self.pump.setTimes(wateringTimes, period, minTemp)
    
    def cleanUp(self):
        self.pump.setState(OnOffState.OFF)      

    def careforplants(self):
          
        print("careforplants for zone: " + self.zoneName)
        
        screen = 0
     
        # Look after plants
        try:  
            print("control watering...")
            self.pump.control()         
      
        except HardwareError as e:
            print("Exception: " + str(e))
            
            statusLight = StatusLight()
            statusLight.setErroredStatus()  
         
            sys.exit("Terminated")
                                   

            
def main():
    
    plantCare = PlantCare("192.168.1.1", "Zone1", 1)
             
    while True:
        plantCare.careforplants()

if __name__ == "__main__":
    main()


