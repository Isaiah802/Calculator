"""
device_smoke.py

Non-interactive smoke test for on-device verification.
Performs:
 - display initialization
 - SD mount and list files
 - show startup.raw if present
 - draw a short verification message on the framebuffer

Run on the device with:
    import device_smoke
"""
import time
try:
    import display_sd
    import sdcard
    import os
    import framebuf
except Exception as e:
    print('This script must run on the MicroPython device:', e)
    raise

W, H = display_sd.W, display_sd.H

def run():
    print('[SMOKE] Initializing display')
    try:
        display_sd.init_disp()
    except Exception as e:
        print('[SMOKE] display init failed:', e)

    print('[SMOKE] Attempting to mount SD and list files')
    try:
        display_sd.spi_to_sd()
        sd = sdcard.SDCard(display_sd.spi, display_sd.cs_sd)
        os.mount(sd, '/sd')
        files = os.listdir('/sd')
        print('[SMOKE] /sd files:', files)
    except Exception as e:
        print('[SMOKE] SD mount/list failed:', e)
        files = []
    finally:
        try: os.umount('/sd')
        except: pass

    # show startup image if present
    try:
        if 'startup.raw' in [f.lower() for f in files]:
            print('[SMOKE] Showing startup.raw')
            display_sd.show_raw_file('/sd/startup.raw')
            time.sleep(1)
    except Exception as e:
        print('[SMOKE] show startup failed:', e)

    # brief framebuffer message
    try:
        buf = bytearray(W * H * 2)
        fb = framebuf.FrameBuffer(buf, W, H, framebuf.RGB565)
        fb.fill(0)
        fb.text('SMOKE TEST', W//2 - 40, H//2 - 6, 1)
        display_sd.spi_to_disp()
        display_sd.window(0, 0, W-1, H-1)
        display_sd.dc(1)
        display_sd.select(display_sd.cs_disp)
        display_sd.spi.write(buf)
        display_sd.deselect(display_sd.cs_disp)
        time.sleep(2)
    except Exception as e:
        print('[SMOKE] framebuffer draw failed:', e)

    print('[SMOKE] Done')

if __name__ == '__main__':
    run()
