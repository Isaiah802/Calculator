"""
Minimal onboard test `main.py` used for hardware diagnostics.

This module is a lightweight, movable copy of the previous top-level
`main.py`. It intentionally avoids heavy imports at module import time
and exposes a `main()` function the top-level shim can call.
"""
import time
from machine import Pin, PWM, SPI
try:
    from drivers.ili9341 import ILI9341
except Exception:
    ILI9341 = None

def run_display_test():
    print('🔧 Running minimal display test...')
    if ILI9341 is None:
        print('⚠️ drivers.ili9341 not available')
        return
    try:
        disp = ILI9341()
        disp.init_display()
        # Create a small color bar pattern
        w, h = 320, 240
        buf = bytearray(w * h * 2)
        # simple gradient: fill with alternating colors
        for i in range(0, len(buf), 2):
            # RGB565 sample: red, green, blue, white
            color = (0xF8, 0x00) if (i // 2) % 4 == 0 else (0x07, 0xE0) if (i // 2) % 4 == 1 else (0x00, 0x1F) if (i // 2) % 4 == 2 else (0xFF, 0xFF)
            buf[i] = color[0]
            buf[i+1] = color[1]
        disp.show_buffer(buf)
        print('✅ Display test image sent')
    except Exception as e:
        print('❌ Display test failed:', e)

def toggle_backlight(pin_no=28):
    try:
        p = PWM(Pin(pin_no))
        p.freq(1000)
        for d in range(0, 65535, 8192):
            p.duty_u16(d)
            time.sleep(0.15)
        for d in range(65535, 0, -8192):
            p.duty_u16(d)
            time.sleep(0.15)
        p.deinit()
        print('✅ Backlight sweep complete')
    except Exception as e:
        print('⚠️ Backlight test failed or not present:', e)

def main():
    """Run the basic hardware diagnostic in a loop.

    Keep everything behind functions to avoid large allocations during
    import time.
    """
    print('🧪 Basic mode starting')
    # Prefer running the finished simple calculator when available.
    try:
        # local import inside main to avoid heavy imports at module import time
        from . import simple_calc
        simple_calc.main()
        return
    except Exception:
        # Fallback: run the hardware diagnostics if calculator not present
        print('ℹ️ simple_calc not available, running display/backlight test')
        run_display_test()
        toggle_backlight()
        print('🔁 Entering idle loop; main_full.py contains the full app')
        while True:
            print('heartbeat')
            time.sleep(5)
