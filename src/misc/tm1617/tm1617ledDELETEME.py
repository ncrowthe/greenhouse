"""TM1617 two-digit 7-segment LED library for MicroPython (STB/CLK/DIO interface).

Usage::

    from tm1617led import TM1617LED

    display = TM1617LED(stb_pin=0, clk_pin=1, dio_pin=2)
    display.show_number(42)    # " 42" -> "42"
    display.show_number(7)     # " 7"
    display.show_number(-5)    # "-5"
    display.clear()
"""

import machine
import time

# TM1617 protocol command registers
CMD_MODE_3G7S = 0x01   # Display mode: 3 grids / 7 segments
CMD_DATA_WRITE = 0x40  # Data setting: write mode, auto-increment address
CMD_START_ADDR = 0xC0  # Address setting: display RAM address 00H
CMD_DISPLAY_ON = 0x88  # Display control: ON; OR with brightness 0-7

RAM_SIZE = 14          # display RAM bytes

# 7-segment patterns for 0-9 (bit0=a ... bit6=g)
_DIGITS = (0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F)
_MINUS = 0x40
_BLANK = 0x00

MIN_NUMBER = -9
MAX_NUMBER = 99


class TM1617LED:
    def __init__(self, stb_pin, clk_pin, dio_pin, brightness=7, digit_addrs=(0, 1)):
        """
        digit_addrs: display RAM address of the (left, right) digit.
        Adjust if your display is wired to different RAM addresses.
        """
        self._stb = machine.Pin(stb_pin, machine.Pin.OUT, value=1)
        self._clk = machine.Pin(clk_pin, machine.Pin.OUT, value=1)
        self._dio = machine.Pin(dio_pin, machine.Pin.OUT, value=1)
        self._brightness = brightness & 0x07
        self._addrs = digit_addrs

        self._send_command(CMD_MODE_3G7S)
        self.clear()

    # ------------------------------------------------------------------
    # Low-level bus
    # ------------------------------------------------------------------

    def _delay(self):
        time.sleep_us(2)

    def _write_byte(self, byte_data):
        """Shift out one byte, LSB first."""
        self._dio.init(mode=machine.Pin.OUT)
        for i in range(8):
            self._clk.value(0)
            self._dio.value((byte_data >> i) & 0x01)
            self._delay()
            self._clk.value(1)
            self._delay()

    def _send_command(self, command):
        self._stb.value(0)
        self._delay()
        self._write_byte(command)
        self._stb.value(1)
        self._delay()

    def _write_ram(self, addr, data):
        """Write one byte to display RAM at addr."""
        self._send_command(CMD_DATA_WRITE)
        self._stb.value(0)
        self._delay()
        self._write_byte(CMD_START_ADDR | addr)
        self._write_byte(data)
        self._stb.value(1)
        self._delay()

    def _apply_display_control(self):
        self._send_command(CMD_DISPLAY_ON | self._brightness)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def brightness(self, level):
        """Set brightness 0 (dimmest) to 7 (brightest) and turn display on."""
        self._brightness = level & 0x07
        self._apply_display_control()

    def off(self):
        """Turn the display off (RAM retained)."""
        self._send_command(0x80)

    def clear(self):
        """Zero all display RAM, blanking the display, and enable output."""
        self._send_command(CMD_DATA_WRITE)
        self._stb.value(0)
        self._delay()
        self._write_byte(CMD_START_ADDR)
        for _ in range(RAM_SIZE):
            self._write_byte(0x00)
        self._stb.value(1)
        self._delay()
        self._apply_display_control()

    def show_raw(self, seg_left, seg_right):
        """Write raw segment bytes (bit0=a ... bit6=g) to the two digits."""
        self._write_ram(self._addrs[0], seg_left & 0xFF)
        self._write_ram(self._addrs[1], seg_right & 0xFF)
        self._apply_display_control()

    def show_number(self, n):
        """
        Show an integer on the two-digit display.

        0..99   -> shown right-aligned, blank leading zero (e.g. " 7", "42")
        -9..-1  -> minus sign in left digit, value in right digit (e.g. "-5")

        Raises ValueError for anything outside -9..99.
        """
        n = int(n)
        if n < MIN_NUMBER or n > MAX_NUMBER:
            raise ValueError("number must be %d..%d" % (MIN_NUMBER, MAX_NUMBER))

        if n < 0:
            left, right = _MINUS, _DIGITS[-n]
        else:
            left = _DIGITS[n // 10] if n >= 10 else _BLANK
            right = _DIGITS[n % 10]
        self.show_raw(left, right)
