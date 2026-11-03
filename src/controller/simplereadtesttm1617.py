import machine
import time

# Pin Definitions
STB_PIN = 17
CLK_PIN = 20
DIO_PIN = 26

# Initialize Pins
stb = machine.Pin(STB_PIN, machine.Pin.OUT, value=1)
clk = machine.Pin(CLK_PIN, machine.Pin.OUT, value=1)
# DIO starts as output, we will switch it dynamically to read
dio = machine.Pin(DIO_PIN, machine.Pin.OUT, value=1)

# TM1617 Commands
CMD_READ_KEY = 0x42  # 01000010: Automatic address increment + Read key data

def tm1617_delay():
    """Enforces chip timing limits (Max clock ~500kHz-1MHz)."""
    time.sleep_us(2)

def write_byte(byte_data):
    """Shifts out 1 byte to the TM1617, LSB First."""
    global dio
    # Ensure DIO is configured as an output
    dio.init(mode=machine.Pin.OUT)
    
    for i in range(8):
        clk.value(0)
        # Extract bit (LSB first)
        bit = (byte_data >> i) & 0x01
        dio.value(bit)
        tm1617_delay()
        
        clk.value(1)
        tm1617_delay()

def read_byte():
    """Reads 1 byte from the TM1617, LSB First."""
    global dio
    byte_data = 0
    
    # CRITICAL: Switch Pico DIO pin to INPUT with a PULL-UP resistor
    # TM1617 has an open-drain output for reading keys
    dio.init(mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
    tm1617_delay()  # Give the line a moment to stabilize
    
    for i in range(8):
        clk.value(0)
        tm1617_delay()  # TM1617 outputs data on the falling clock edge
        
        # Read the bit state
        bit = dio.value()
        if bit:
            byte_data |= (1 << i)
            
        clk.value(1)
        tm1617_delay()
        
    return byte_data

def read_buttons():
    """Reads the button matrix from the TM1617."""
    stb.value(0)       # Start communication
    tm1617_delay()
    
    write_byte(CMD_READ_KEY)  # Send the 'Read Keys' instruction
    
    # TM1617 returns up to 5 bytes of key matrix data depending on configuration.
    # For a simple test, we will read the first 2 bytes.
    key_byte1 = read_byte()
    key_byte2 = read_byte()
    key_byte3 = read_byte()
    key_byte4 = read_byte()
    key_byte5 = read_byte()

    
    stb.value(1)       # End communication
    return key_byte1, key_byte2, key_byte3, key_byte4, key_byte5

# --- Main Loop ---
print("Starting TM1617 Button Reader Loop...")

try:
    while True:
        b1, b2, b3, b4, b5 = read_buttons()
        
        # If any bit is 1, a button in the matrix is pressed
        #if b1 != 0 or b2 != 0:
        print(f"Button Pressed! Byte 1: {bin(b1)} | Byte 2: {bin(b2)} | Byte 3: {bin(b3)} | Byte 4: {bin(b4)} | Byte 5: {bin(b5)}")
            
        time.sleep(1)  # Poll 10 times a second

except KeyboardInterrupt:
    print("Program stopped.")
