import machine  # Import hardware control module
import time  # Import time module


class Joystick(object):
    
    def __init__(self):
    
        GP27 = 27
        GP26 = 26
        GP22 = 22
        # Initialize X and Y axes of the joystick
        self.x_joystick = machine.ADC(GP27)
        self.y_joystick = machine.ADC(GP26)

        # Initialize joystick switch with pull-up resistor
        self.z_switch = machine.Pin(GP22, machine.Pin.IN, machine.Pin.PULL_UP)
        
        self.x_point = 0        
        self.y_point = 0
        self.z_fire = 0
        self.z_long_press = False
        self._last_z_press_time = None
        self._last_z_state = 1
        self._long_press_reported = False

    def _time_ms(self):
        if hasattr(time, 'ticks_ms'):
            return time.ticks_ms()
        return int(time.time() * 1000)

    def detectLongPress(self, threshold_ms=2000):
        """Detect a long press on the joystick button.

        Returns True when the button is held down longer than threshold_ms.
        """
        current_z = self.z_switch.value()
        current_time = self._time_ms()
        long_pressed = False

        if current_z == 0:
            if self._last_z_state == 1:
                self._last_z_press_time = current_time
                self._long_press_reported = False
            elif self._last_z_press_time is not None and not self._long_press_reported:
                elapsed = current_time - self._last_z_press_time
                if elapsed >= threshold_ms:
                    long_pressed = True
                    self._long_press_reported = True
        else:
            self._last_z_press_time = None
            self._long_press_reported = False

        self._last_z_state = current_z
        self.z_long_press = long_pressed
        return long_pressed

    def scan(self):
        
        x = self.x_joystick.read_u16()  # Read X-axis value
        y = self.y_joystick.read_u16()  # Read Y-axis value
        z = self.z_switch.value()  # Read switch state

        # Print joystick values and switch state
        #print("X: ", x, " Y: ", y)
        #print("SW: ", z)
        
        if (x > 40000):
            print("DOWN")
            if self.x_point < 40:            
                self.x_point = self.x_point + 1
            
        if (x < 30000):
            print("UP")
            if self.x_point > -5:            
                self.x_point = self.x_point - 1
            
        if (y > 40000):
            print("LEFT")
            if self.y_point > -5:
                self.y_point = self.y_point - 1
            
        if (y < 20000):
            print("RIGHT")
            if self.y_point < 50:
                self.y_point = self.y_point + 1
                
        if (z == 0):
            print("FIRE!")
            self.z_fire = True
        else:
            self.z_fire = False            
  
        if self.detectLongPress():
            print("LONG Press!")
            self.z_long_press = True
        else:
            self.z_long_press = False

        result = (self.x_point, self.y_point, self.z_fire, self.z_long_press)
        
        return result
            
def main():
    
    joystick = Joystick()
        
    while True:
        point = joystick.scan()
        
        #print(point)
        
        time.sleep_ms(100)
        
if __name__ == "__main__":
    main()            
                
                


