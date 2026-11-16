import time

from tm1617 import TM1617LED


def main():
    display = TM1617LED(stb_pin=0, clk_pin=1, dio_pin=2)

    # Count down from 50 to -10 (inclusive), one number per half second.
    for n in range(50, -11, -1):
        try:
            display.show_number(n)
            print("Displaying", n)
        except ValueError as e:
            # Display only supports -9..99; it shows "Er" before raising.
            print("Cannot display", n, "-", e)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
