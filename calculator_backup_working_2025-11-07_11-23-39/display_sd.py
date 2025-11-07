
# display_sd.py
import sdcard
import os
import time
from machine import Pin, SPI
try:
    # PWM is optional on some MicroPython builds; use if available for backlight
    from machine import PWM
    HAVE_PWM = True
except Exception:
    PWM = None
    HAVE_PWM = False

# ---------- HARDWARE SETUP ----------
spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
cs_disp = Pin(13, Pin.OUT, value=1)
dc = Pin(15, Pin.OUT)
rst = Pin(14, Pin.OUT)
cs_sd = Pin(17, Pin.OUT, value=1)
led = Pin(28, Pin.OUT)
# optional PWM object for smooth brightness control
_led_pwm = None

W, H = 320, 240
BUF_SIZE = 512

# ---------- HELPERS ----------
def select(cs): cs(0)
def deselect(cs): cs(1)

def spi_to_sd():
    spi.init(baudrate=1_000_000, polarity=0, phase=0)
    deselect(cs_disp)
    deselect(cs_sd)

def spi_to_disp():
    spi.init(baudrate=32_000_000, polarity=0, phase=0)
    deselect(cs_disp)
    deselect(cs_sd)

# ---------- DISPLAY COMMANDS ----------
def cmd(c):
    dc(0)
    select(cs_disp)
    spi.write(bytes([c]))
    deselect(cs_disp)

def data_write(b):
    dc(1)
    select(cs_disp)
    spi.write(b)
    deselect(cs_disp)

def init_disp():
    rst(0); time.sleep_ms(50)
    rst(1); time.sleep_ms(120)
    cmd(0x01); time.sleep_ms(150)
    cmd(0x11); time.sleep_ms(500)
    cmd(0x3A); data_write(b'\x55')  # 16-bit color
    cmd(0x36); data_write(b'\x28')  # MADCTL: RGB, row/col order
    cmd(0x29); time.sleep_ms(100)
    # Turn on LED backlight at full brightness for dev by default
    try:
        set_brightness(100)
    except Exception:
        try:
            led(1)
        except Exception:
            pass


def set_brightness(percent: int):
    """Set backlight brightness (0-100).

    Uses PWM on the backlight pin if available. If PWM is not available,
    treat percent >= 50 as ON and <50 as OFF. This keeps compatibility with
    minimal MicroPython builds and our dev requirement to set 100% brightness.
    """
    global _led_pwm
    # clamp
    if percent < 0: percent = 0
    if percent > 100: percent = 100

    if HAVE_PWM:
        try:
            if _led_pwm is None:
                _led_pwm = PWM(led)
                # Typical RP2040 PWM freq for backlight control
                _led_pwm.freq(1000)
            # Convert percent to duty (0-65535)
            duty = int(percent * 65535 // 100)
            _led_pwm.duty_u16(duty)
        except Exception as e:
            # fallback to digital on/off
            if percent >= 50:
                led(1)
            else:
                led(0)
    else:
        # No PWM available: binary on/off
        if percent >= 50:
            led(1)
        else:
            led(0)

def window(x0, y0, x1, y1):
    cmd(0x2A)
    data_write(bytes([x0>>8, x0&0xFF, x1>>8, x1&0xFF]))
    cmd(0x2B)
    data_write(bytes([y0>>8, y0&0xFF, y1>>8, y1&0xFF]))
    cmd(0x2C)

# ---------- IMAGE DISPLAY ----------
def show_raw_file(path, back_button=None):
    """
    Display a .raw file from SD card.
    back_button: a function that returns True when user presses 'back'
    """
    spi_to_sd()
    try:
        sd = sdcard.SDCard(spi, cs_sd)
        os.mount(sd, "/sd")
    except Exception as e:
        print("❌ Failed to mount SD:", e)
        return False

    # Load image in chunks
    image_data = []
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(BUF_SIZE)
                if not chunk:
                    break
                if len(chunk) < BUF_SIZE:
                    chunk += b'\x00\x00' * ((BUF_SIZE - len(chunk)) // 2)
                image_data.append(chunk)
    except Exception as e:
        print("❌ Failed to read file:", e)
        os.umount("/sd")
        return False
    finally:
        os.umount("/sd")

    # Send to display
    spi_to_disp()
    window(0, 0, W-1, H-1)
    dc(1)
    select(cs_disp)
    for chunk in image_data:
        spi.write(chunk)
        # Check back button during display
        if back_button and back_button():
            deselect(cs_disp)
            return True
    deselect(cs_disp)
    return True

# ---------- SD FILE LIST ----------
def list_raw_files():
    spi_to_sd()
    files = []
    try:
        sd = sdcard.SDCard(spi, cs_sd)
        os.mount(sd, "/sd")
        files = [f for f in os.listdir("/sd") if f.lower().endswith(".raw")]
        files.sort()
    except Exception as e:
        print("❌ SD error:", e)
    finally:
        try: os.umount("/sd")
        except: pass
    return files

# ---------- STARTUP IMAGE ----------
def show_startup_image(filename="startup.raw"):
    """
    Display a startup image on boot.
    """
    try:
        show_raw_file(f"/sd/{filename}")
    except Exception as e:
        print("⚠️ Startup image failed:", e)
        
def play_animation(folder, fps=10, back_button=None):
    """
    Play raw frames from a folder as an animation.
    MicroPython-compatible (no os.path).
    """
    import os
    import time

    frame_delay = 1 / fps

    # List all .raw files in order
    try:
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".raw")])
    except Exception as e:
        print("❌ Failed to list frames:", e)
        return

    if not files:
        print("⚠️ No frames found in folder:", folder)
        return

    # Loop through frames
    for fname in files:
        path = folder + "/" + fname  # <-- manual concatenation

        # Check for back button before displaying
        if back_button and back_button():
            print("⏹️ Animation interrupted by back button")
            return

        # Display frame
        show_raw_file(path)

        # Wait for frame delay, checking back button
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < frame_delay*1000:
            if back_button and back_button():
                print("⏹️ Animation interrupted by back button")
                return
            time.sleep_ms(5)

