# TM1617 LED display + key driver for MicroPython
# Protocol: TM1637-compatible 2-wire serial (CLK + DIO), LSB-first
#
# The TM1617 drives a 2-digit 7-segment LED display and reads 3 buttons.
#
# Command summary:
#   Data command   0x40  write data to display RAM, auto-increment address
#   Address command0xC0 + addr  set starting address (0x00, 0x01 for 2 digits)
#   Display control0x80 | (on<<3) | brightness  brightness 0-7, bit3 = on/off
#   Key read       0x42  read 1 byte of key data

from machine import Pin
import time

# 7-segment encoding for digits 0-9 and A-F (segments: gfedcba)
_DIGITS = (
    0x3F, 0x06, 0x5B, 0x4F, 0x66,  # 0 1 2 3 4
    0x6D, 0x7D, 0x07, 0x7F, 0x6F,  # 5 6 7 8 9
    0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71,  # A b C d E F
)

_CMD_DATA    = 0x40  # write mode, auto-increment
_CMD_KEY     = 0x42  # read key data
_CMD_ADDR    = 0xC0  # address base
_CMD_DISPLAY = 0x80  # display control base

_DELAY_US = 10  # half-period for CLK, microseconds


class TM1617:
    """
    Driver for the TM1617 2-digit 7-segment LED display + 3-button controller.

    Usage::

        from tm1617driver import TM1617
        display = TM1617(clk_pin=0, dio_pin=1)
        display.brightness(7)        # 0-7
        display.show_number(42)      # shows "42"
        display.show_raw(0x06, 0x5B) # digit0='1', digit1='2'
        keys = display.read_keys()   # returns dict {1: bool, 2: bool, 3: bool}
    """

    def __init__(self, clk_pin, dio_pin, brightness=7):
        self._clk = Pin(clk_pin, Pin.OUT, value=1)
        self._dio = Pin(dio_pin, Pin.OPEN_DRAIN, value=1)
        self._brightness = brightness & 0x07
        self._on = True

    # ------------------------------------------------------------------
    # Low-level bus primitives
    # ------------------------------------------------------------------

    def _delay(self):
        time.sleep_us(_DELAY_US)

    def _start(self):
        """Bus start condition: DIO falls while CLK is high."""
        self._dio(1)
        self._clk(1)
        self._delay()
        self._dio(0)
        self._delay()
        self._clk(0)
        self._delay()

    def _stop(self):
        """Bus stop condition: DIO rises while CLK is high."""
        self._dio(0)
        self._clk(0)
        self._delay()
        self._clk(1)
        self._delay()
        self._dio(1)
        self._delay()

    def _write_byte(self, byte):
        """Clock out 8 bits LSB-first, then read ACK."""
        for _ in range(8):
            self._dio(byte & 0x01)
            byte >>= 1
            self._delay()
            self._clk(1)
            self._delay()
            self._clk(0)
            self._delay()
        # ACK: release DIO and read; chip pulls low to acknowledge
        self._dio(1)
        self._clk(1)
        self._delay()
        ack = self._dio()   # 0 = ACKed
        self._clk(0)
        self._delay()
        return ack == 0

    def _read_byte(self):
        """Clock in 8 bits LSB-first, then send NAK (DIO stays high)."""
        byte = 0
        self._dio(1)        # release DIO for reading
        for i in range(8):
            self._clk(0)
            self._delay()
            self._clk(1)
            self._delay()
            if self._dio():
                byte |= (1 << i)
        # NAK: hold DIO high
        self._clk(0)
        self._delay()
        self._clk(1)
        self._delay()
        self._clk(0)
        self._delay()
        return byte

    # ------------------------------------------------------------------
    # High-level commands
    # ------------------------------------------------------------------

    def _send_command(self, cmd):
        self._start()
        self._write_byte(cmd)
        self._stop()

    def _write_display(self, seg0, seg1):
        """Write raw segment bytes to address 0x00 and 0x01."""
        # Data command: auto-increment, write mode
        self._send_command(_CMD_DATA)
        # Address + data
        self._start()
        self._write_byte(_CMD_ADDR | 0x00)
        self._write_byte(seg0)
        self._write_byte(seg1)
        self._stop()
        # Display control
        ctrl = _CMD_DISPLAY | (0x08 if self._on else 0x00) | self._brightness
        self._send_command(ctrl)

    def _apply_display_ctrl(self):
        ctrl = _CMD_DISPLAY | (0x08 if self._on else 0x00) | self._brightness
        self._send_command(ctrl)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def brightness(self, level):
        """Set brightness 0 (dimmest) to 7 (brightest)."""
        self._brightness = level & 0x07
        self._apply_display_ctrl()

    def on(self):
        """Turn display on."""
        self._on = True
        self._apply_display_ctrl()

    def off(self):
        """Turn display off (data retained in RAM)."""
        self._on = False
        self._apply_display_ctrl()

    def clear(self):
        """Blank both digits."""
        self._write_display(0x00, 0x00)

    def show_raw(self, seg0, seg1):
        """
        Write raw 7-segment bytes directly.

        Segment bit mapping (standard TM163x compatible):
          bit 0 = a (top)
          bit 1 = b (top-right)
          bit 2 = c (bottom-right)
          bit 3 = d (bottom)
          bit 4 = e (bottom-left)
          bit 5 = f (top-left)
          bit 6 = g (middle)
          bit 7 = decimal point (if wired)
        """
        self._write_display(seg0 & 0xFF, seg1 & 0xFF)

    def show_number(self, n):
        """
        Display a two-digit integer (0-99).
        Leading zero is shown for values < 10.
        """
        n = max(0, min(n, 99))
        tens = n // 10
        ones = n % 10
        self._write_display(_DIGITS[tens], _DIGITS[ones])

    def show_hex(self, n):
        """
        Display a two-digit hex value (0x00-0xFF).
        """
        n = max(0, min(n, 0xFF))
        self._write_display(_DIGITS[(n >> 4) & 0xF], _DIGITS[n & 0xF])

    def show_chars(self, char0, char1):
        """
        Display two characters from '0'-'9' or 'A'-'F' / 'a'-'f'.
        Unknown characters are blanked (0x00).
        """
        def _encode(c):
            c = c.upper()
            if '0' <= c <= '9':
                return _DIGITS[ord(c) - ord('0')]
            if 'A' <= c <= 'F':
                return _DIGITS[10 + ord(c) - ord('A')]
            return 0x00
        self._write_display(_encode(char0), _encode(char1))

    def read_keys(self):
        """
        Read the three button states.

        Returns a dict: {1: bool, 2: bool, 3: bool}
        True means the button is currently pressed.

        Key byte bit mapping (TM1617 typical):
          bit 0 = K1
          bit 1 = K2
          bit 2 = K3
        """
        self._start()
        self._write_byte(_CMD_KEY)
        raw = self._read_byte()
        self._stop()
        return {
            1: bool(raw & 0x01),
            2: bool(raw & 0x02),
            3: bool(raw & 0x04),
        }
