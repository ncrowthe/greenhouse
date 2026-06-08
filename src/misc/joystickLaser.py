from machine import Pin, PWM
from math import floor
import time
import math
from Joystick import Joystick
 
##############################
    
class ServoMotor(object):

    def __init__(self, pin): 
        # Initialize PWM on pin 16 for servo control
        self.servo = machine.PWM(machine.Pin(pin))
        self.servo.freq(50)  # Set PWM frequency to 50Hz, common for servo motors


    """
    Maps a value from one range to another.
    This function is useful for converting servo angle to pulse width.

    Args:
        x (int): The input value to be mapped.
        in_min (int): The minimum value of the input range.
        in_max (int): The maximum value of the input range.
        out_min (int): The minimum value of the output range.
        out_max (int): The maximum value of the output range.

    Returns:
        int: The mapped value.
    """
    def interval_mapping(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    """
    Moves the servo to a specific angle.
    The angle is converted to a suitable duty cycle for the PWM signal.

    Args:
        angle (int): The angle to move the servo to.

    Returns:
        None
    """    
    def servo_write(self, angle):
        
        pulse_width = self.interval_mapping(
            angle, 0, 180, 0.5, 2.5
        )  # Map angle to pulse width in ms
        duty = int(
            self.interval_mapping(pulse_width, 0, 20, 0, 65535)
        )  # Map pulse width to duty cycle
        self.servo.duty_u16(duty)  # Set PWM duty cycle

    """
    Tick.

    Returns:
        None
    """
    def tick(self, pos):                        
        
        OFFSET = 60      
        self.servo_write(OFFSET + pos)
 
#######################

def createSemiCircle():
    
    a = 2
    b = 3
    r = 3

    #The lower this value the higher quality the circle is with more points generated
    stepSize = 0.109

    #Generated vertices
    positions = []

    t = 2
    while t < 2 * math.pi:
        positions.append((((r * math.cos(t) + a) * 4), (r * math.sin(t) + b) * 4))
        t += stepSize

    print("LEN: " + str(len(positions)))
    print("Positions: " + str(positions))
    
    return positions
    

def display(point):
    print("%3d, %3d, %3d, %3d" % point) # print position
            
# Continuously display current time every second 
def main():
    
    redledPin = 0 #"Red LED"
    redled = machine.Pin(redledPin, machine.Pin.OUT)

    joystick = Joystick()
    servoMotorX = ServoMotor(16)
    servoMotorY = ServoMotor(17)
    
    positions = createSemiCircle()
    
    while True:
        
        point = joystick.scan()
        
        display(point)

        servoMotorX.tick(point[0])
        servoMotorY.tick(point[1])
        
        redled.value(point[2])  #turn on the Laser if button fired                 
            
        if (point[3]): # Long press
            redled.value(True)  #turn on the Laser
            
            for point in reversed(positions):
                servoMotorX.tick(point[0])
                servoMotorY.tick(point[1])    
                time.sleep_ms(100)  # One second
                
            for point in positions:
                time.sleep_ms(50)  # One second
                redled.value(False)  #turn off the Laser
                time.sleep_ms(50)  # One second
                redled.value(True)  #turn on the Laser              
                       
            
        time.sleep_ms(10)  # One second
                    
    
if __name__ == "__main__":
    main()                                                                                                                                                                      


