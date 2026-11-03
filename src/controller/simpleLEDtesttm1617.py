import machine
import time

# Pin Definitions (Match your physical wiring)
STB_PIN = 17
CLK_PIN = 20
DIO_PIN = 26


# Initialize Pins
stb = machine.Pin(STB_PIN, machine.Pin.OUT, value=1)
clk = machine.Pin(CLK_PIN, machine.Pin.OUT, value=1)
dio = machine.Pin(DIO_PIN, machine.Pin.OUT, value=1)

# TM1617 Protocol Command Registers
CMD_MODE_3G7S = 0x01      # Display Mode: 3 Grids / 7 Segments
CMD_DATA_WRITE = 0x40     # Data Setting: Write mode, auto-increment address
CMD_START_ADDR = 0xC0     # Address Setting: Start at Display RAM Address 00H
CMD_DISPLAY_ON = 0x8F     # Display Control: Display ON, Max Brightness (14/16 pulse)

def tm1617_delay():
    """Maintains consistent timing parameters so the Pico does not overrun the IC."""
    time.sleep_us(2)

def write_byte(byte_data):
    """Shifts out exactly 1 byte of information, LSB First."""
    # Enforce output mode on the shared data line
    dio.init(mode=machine.Pin.OUT)
    
    for i in range(8):
        clk.value(0)
        # Isolate the bit from Least Significant to Most Significant
        bit = (byte_data >> i) & 0x01
        dio.value(bit)
        tm1617_delay()
        
        clk.value(1)
        tm1617_delay()

def send_command(command):
    """Helper macro to handle brief control parameter pulses."""
    stb.value(0)
    tm1617_delay()
    write_byte(command)
    stb.value(1)
    tm1617_delay()

def clear_display():
    """Flushes all RAM registers to zero, clearing residual artifacts."""
    send_command(CMD_DATA_WRITE)
    stb.value(0)
    tm1617_delay()
    write_byte(CMD_START_ADDR)
    # The TM1617 has 14 display register bytes; clear them all
    for _ in range(14):
        write_byte(0x00)
    stb.value(1)
    tm1617_delay()

def turn_on_all_lights():
    """Fills data structures to pull all output drivers active."""
    # 1. Inform the controller of an upcoming stream
    send_command(CMD_DATA_WRITE)
    
    # 2. Open the memory window and dump high bits
    stb.value(0)
    tm1617_delay()
    write_byte(CMD_START_ADDR)
    
    # 0xFF (binary 11111111) forces all associated segment anodes high
    for _ in range(6):  
        write_byte(0x00)
        
    stb.value(1)
    tm1617_delay()

# --- Execution sequence ---
print("Configuring TM1617 display settings...")

# 1. Select the configuration matrix
send_command(CMD_MODE_3G7S)

# 2. Reset the lines to guarantee a clean baseline
clear_display()
time.sleep(0.5)

# 3. Deliver the active illumination states
print("Illuminating all connected LEDs...")
turn_on_all_lights()

# 4. Enable the display gating mechanism and trigger brightness
send_command(CMD_DISPLAY_ON)

print("Display pipeline active.")
