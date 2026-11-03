from tm1617 import TM1617

d = TM1617(clk_pin=20, dio_pin=26)
#d.brightness(3)          # 0–7
#d.show_number(42)        # integer 0–99
#d.show_hex(0xAB)         # hex 00–FF → "Ab"
#d.show_chars('0', '1')   # any 0-9 / A-F character
#d.show_raw(0x3F, 0x06)   # raw segment bytes
#d.clear()
#d.off()

keys = d.read_keys()     # {1: bool, 2: bool, 3: bool}

print (keys)