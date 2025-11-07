"""
input.py

Key scanning and keymaps extracted from original firmware.

This module is MicroPython-specific and expects `machine.Pin` to be
available. It exposes:
  - Keys class instance `km` with method `get_events()` returning list of ((ri,ci), kind)
  - `base` and `shift` key maps mapping (row_index,col_index) -> label

Usage: import input; events = input.km.get_events(); label = input.base.get(k)
"""

try:
    from machine import Pin
    import time as _time
except Exception as e:
    raise ImportError("input.py requires MicroPython 'machine' module")

# Hardware keypad mapping (rows/cols are GPIO numbers)
COLS = [2,3,4,5]
ROWS = [6,7,8,9,21,27]

# Initialize row pins as outputs and drive them high by default
rows = []
for r in ROWS:
    rp = Pin(r, Pin.OUT)
    rp.value(1)
    rows.append(rp)
# Column pins as inputs with pull-ups
cols = [Pin(c, Pin.IN, Pin.PULL_UP) for c in COLS]

DEB_MS = 40
LONG_MS = 600

class Keys:
    def __init__(self):
        self._pressed = set()
        self._t_down = {}

    def scan_now(self):
        pressed = set()
        # drive each row low in turn to detect column hits
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

# Key maps (row, col) -> label
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
