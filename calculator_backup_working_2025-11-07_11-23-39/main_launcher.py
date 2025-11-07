"""
main_launcher.py

Thin device/host launcher that wires `ModeMenu` to simple device-capable handlers.

Behavior:
 - If run on a host (regular Python), it runs in console mode (use n/p/s to navigate).
 - If run on a MicroPython device, it will attempt to initialize the display and
   provide simple placeholders that use `display_sd` functions. This file is
   intentionally conservative: it doesn't import or execute the large `main.py`
   firmware; instead it provides adapters so we can progressively implement
   full modes.

Run on host for quick testing:
    python main_launcher.py

On device: copy this file and `mode_menu.py`, then run via REPL or at boot.
"""

try:
    from mode_menu import ModeMenu, placeholder_mode
except Exception:
    # Fallback embedded ModeMenu for devices that don't have `mode_menu.py`
    import time as _time

    class ModeMenu:
        def __init__(self, items):
            self.items = list(items)
            self.index = 0
            self.ctx = {'running': True}

        def move_next(self):
            self.index = (self.index + 1) % len(self.items)

        def move_prev(self):
            self.index = (self.index - 1) % len(self.items)

        def select(self):
            label, handler = self.items[self.index]
            print(f"[MENU] Entering: {label}")
            try:
                handler(self.ctx)
            except Exception as e:
                print(f"[MENU] Handler '{label}' raised:", e)
            print(f"[MENU] Returned from: {label}")

        def draw(self):
            print('\n' + '=' * 40)
            print('Mode Menu:')
            for i, (label, _) in enumerate(self.items):
                prefix = '>' if i == self.index else ' '
                print(f" {prefix} {label}")
            print('=' * 40)

    def placeholder_mode(name, hold_seconds=1):
        def handler(ctx):
            print(f"[{name}] started (placeholder).")
            try:
                _time.sleep(hold_seconds)
            except Exception:
                pass
            print(f"[{name}] exiting")
        return handler
import sys

# Try to detect MicroPython vs CPython
IS_MICROPY = sys.implementation.name.lower().startswith('micropython') if hasattr(sys, 'implementation') else False

if IS_MICROPY:
    # MicroPython-specific imports
    import display_sd
    # Try the historical module name 'input', but some environments may block that
    # name. Fall back to a safer 'keypad' module if present.
    input_mod = None
    HAVE_INPUT = False
    try:
        import input as input_mod
        HAVE_INPUT = True
    except Exception:
        try:
            import keypad as input_mod
            HAVE_INPUT = True
        except Exception:
            # Try to bootstrap an embedded `input` implementation by executing
            # the keypad source into a module; this helps when filesystem
            # imports are unreliable on some device setups.
            try:
                INPUT_SRC = '''
try:
    from machine import Pin
    import time as _time
except Exception as e:
    raise ImportError("input.py requires MicroPython 'machine' module")

COLS = [2,3,4,5]
ROWS = [6,7,8,9,21,27]

rows = []
for r in ROWS:
    rp = Pin(r, Pin.OUT)
    rp.value(1)
    rows.append(rp)
cols = [Pin(c, Pin.IN, Pin.PULL_UP) for c in COLS]

DEB_MS = 40
LONG_MS = 600

class Keys:
    def __init__(self):
        self._pressed = set()
        self._t_down = {}

    def scan_now(self):
        pressed = set()
        for rpin in rows: rpin.value(1)
        for ri, r in enumerate(rows):
            for rpin in rows: rpin.value(1)
            r.value(0); _time.sleep_us(5)
            for ci, c in enumerate(cols):
                if c.value() == 0: pressed.add((ri,ci))
        return pressed

    def get_events(self):
        now = _time.ticks_ms()
        pressed = self.scan_now()
        events = []
        for k in pressed:
            if k in self._pressed:
                continue
            if k not in self._t_down:
                self._t_down[k] = now
                continue
            if _time.ticks_diff(now, self._t_down[k]) >= DEB_MS:
                self._pressed.add(k)
                events.append((k, 'down'))

        for k in list(self._pressed):
            if k not in pressed:
                t0 = self._t_down.pop(k, now)
                dur = _time.ticks_diff(now, t0)
                self._pressed.remove(k)
                kind = 'long' if dur >= LONG_MS else 'tap'
                events.append((k, kind))

        for k in list(self._t_down):
            if k not in pressed and k not in self._pressed:
                self._t_down.pop(k, None)

        return events

km = Keys()

base = {
    (5,0):'ON', (5,1):'=',  (5,2):'.',  (5,3):'0',
    (4,0):'+',  (4,1):'3',  (4,2):'2',  (4,3):'1',
    (3,0):'-',  (3,1):'6',  (3,2):'5',  (3,3):'4',
    (2,0):'*',  (2,1):'9',  (2,2):'8',  (2,3):'7',
    (1,0):'/',  (1,1):')',  (1,2):'(',  (1,3):'C',
    (0,0):'Save',(0,1):'DEL',(0,2):'π', (0,3):'S'
}

shift = base.copy(); shift.update({
    (5,0):'ON',  (5,1):'=',    (5,2):'.',    (5,3):'0',
    (4,0):'+',   (4,1):'tan(', (4,2):'cos(', (4,3):'sin(',
    (3,0):'/',   (3,1):'^2',   (3,2): 'ln(',  (3,3):'log(',
    (2,0):'*',   (2,1):'9',    (2,2):'8',    (2,3):'7',
    (1,0):'√',   (1,1):')',    (1,2):'(',    (1,3):'C',
    (0,0):'exp(', (0,1):'DEL', (0,2):'π',    (0,3):'S'
})

def label_for(k, shift_on=False):
    return (shift if shift_on else base).get(k)
'''
                mod_ns = {}
                exec(INPUT_SRC, mod_ns)
                class _M: pass
                mod = _M()
                for k,v in mod_ns.items():
                    setattr(mod, k, v)
                input_mod = mod
                HAVE_INPUT = True
            except Exception as e:
                print('[LAUNCHER] input bootstrap failed:', e)
                input_mod = None
                HAVE_INPUT = False
    import calculator
    import framebuf
    import time

    W, H = display_sd.W, display_sd.H

    # create a framebuffer like the original firmware
    buf = bytearray(W * H * 2)
    fb = framebuf.FrameBuffer(buf, W, H, framebuf.RGB565)

    # Ensure backlight is at 100% for development convenience
    try:
        display_sd.set_brightness(100)
    except Exception:
        # set_brightness may not exist on older display_sd; ignore
        pass

    def show():
        # Use display_sd helpers to send the frame buffer to the TFT
        display_sd.spi_to_disp()
        display_sd.window(0, 0, W-1, H-1)
        display_sd.dc(1)
        display_sd.select(display_sd.cs_disp)
        display_sd.spi.write(buf)
        display_sd.deselect(display_sd.cs_disp)

    # Device/context to pass to handlers
    def make_ctx():
        return {
            'fb': fb,
            'show': show,
            'km': input_mod.km,
            'base': input_mod.base,
            'shift': input_mod.shift,
            'W': W,
            'H': H,
        }

    def files_handler(ctx):
        try:
            files = display_sd.list_raw_files()
            print('[files_handler] files:', files)
            # show simple text on framebuffer
            fb.fill(0)
            fb.text('Files on /sd:', 8, 8, 1)
            y = 24
            for f in files[:10]:
                fb.text(f[:30], 8, y, 1); y += 12
            show()
        except Exception as e:
            print('[files_handler] error:', e)

    def games_handler(ctx):
        # placeholder: leave for future integration
        fb.fill(0)
        fb.text('Games (placeholder)', 20, H//2 - 6, 1)
        show()

    def settings_handler(ctx):
        fb.fill(0)
        fb.text('Settings (placeholder)', 10, H//2 - 6, 1)
        show()

    # Register handlers; Calculator uses the new calculator module and will be
    # passed a ctx with fb/show/km so it can run on-device. Other handlers are
    # conservative placeholders for now.
    # Register handlers; Calculator uses the new calculator module and will be
    # passed a ctx with fb/show/km so it can run on-device. File Browser now
    # uses the dedicated file_browser module for safer SD operations.
    import file_browser

    items = [
        ('Calculator', lambda ctx: calculator.calc_handler(make_ctx())),
        ('File Browser', lambda ctx: file_browser.file_browser_handler(make_ctx())),
        ('Graph', placeholder_mode('Graph', 0.5)),
        ('Games', games_handler),
        ('Settings', settings_handler),
    ]

    menu = ModeMenu(items)

    # On-device: navigate the menu with the keypad. Keys:
    #  - '2' : up, '8' : down, '=' : select, 'C' : back (if a mode supports it),
    #  - 'S' : shift modifier toggles behavior in modes.
    shift_on = False
    try:
        if not HAVE_INPUT:
            print('[LAUNCHER] Running in MicroPython mode, but keypad/input module not available.')
            # Draw the menu once to the framebuffer (if display available) and exit
            try:
                fb.fill(0)
                fb.text('Mode Menu (keypad missing)', 8, 8, 1)
                y = 30
                for i, (label, _) in enumerate(items):
                    fb.text(label, 8, y, 1); y += 12
                show()
            except Exception as e:
                print('[LAUNCHER] draw error:', e)
        else:
            print('[LAUNCHER] Running in MicroPython mode: keypad navigation enabled')
            while True:
                menu.draw()
                # poll keys
                events = input_mod.km.get_events()
                if not events:
                    time.sleep(0.02); continue
                for (k, kind) in events:
                    lbl = input_mod.label_for(k, shift_on)
                    if not lbl: continue
                    if lbl == '2' and kind == 'tap':
                        menu.move_prev(); menu.draw(); continue
                    if lbl == '8' and kind == 'tap':
                        menu.move_next(); menu.draw(); continue
                    if lbl == 'S' and kind == 'tap':
                        shift_on = not shift_on; menu.draw(); continue
                    if lbl == '=' and kind == 'tap':
                        # call the selected handler with a device ctx
                        menu.select(); menu.draw(); continue
    except KeyboardInterrupt:
        print('[LAUNCHER] Interrupted')

else:
    # Host mode: use console navigation from ModeMenu
    items = [
        ('Calculator', placeholder_mode('Calculator', 0.5)),
        ('File Browser', placeholder_mode('File Browser', 0.5)),
        ('Graph', placeholder_mode('Graph', 0.5)),
        ('Games', placeholder_mode('Games', 0.5)),
        ('Settings', placeholder_mode('Settings', 0.5)),
    ]
    menu = ModeMenu(items)
    menu.run_console()
