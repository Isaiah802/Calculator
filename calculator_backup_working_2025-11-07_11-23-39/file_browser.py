"""
file_browser.py

Provides safe SD operations and a basic interactive file browser handler
for the Pico. Handler is conservative and MicroPython-focused; it expects a
ctx dict with 'fb','show','km','base','shift','W','H'.

Functions:
  - safe_mount(), safe_umount()
  - list_files(folder='/sd')
  - delete_file(name)
  - rename_file(old,new)
  - write_line(path,line)
  - file_browser_handler(ctx)

The handler supports: 2/8 move, '=' open, DEL delete (confirmation), C back.
"""

import time
import sdcard
import os
import display_sd

def safe_mount(retries=2):
    """Attempt to mount the SD card at /sd. Returns True on success."""
    try:
        display_sd.spi_to_sd()
        sd = sdcard.SDCard(display_sd.spi, display_sd.cs_sd)
        try:
            os.mount(sd, '/sd')
        except Exception:
            # maybe already mounted; ignore
            pass
        return True
    except Exception as e:
        # try simple retry
        for _ in range(retries):
            try:
                time.sleep(0.5)
                display_sd.spi_to_sd()
                sd = sdcard.SDCard(display_sd.spi, display_sd.cs_sd)
                try:
                    os.mount(sd, '/sd')
                except Exception:
                    pass
                return True
            except Exception:
                continue
    return False

def safe_umount():
    try:
        os.umount('/sd')
    except Exception:
        pass

def list_files(folder='/sd'):
    """Return sorted list of non-hidden files in folder or [] on error."""
    if not safe_mount():
        return []
    try:
        items = os.listdir(folder)
        items = [i for i in items if not i.startswith('.')]
        items.sort()
        return items
    except Exception:
        return []
    finally:
        safe_umount()

def delete_file(name):
    if not safe_mount(): return False
    try:
        os.remove('/sd/' + name)
        return True
    except Exception:
        return False
    finally:
        safe_umount()

def rename_file(old, new):
    if not safe_mount(): return False
    try:
        os.rename('/sd/' + old, '/sd/' + new)
        return True
    except Exception:
        return False
    finally:
        safe_umount()

def write_line(path, line):
    if not safe_mount(): return False
    try:
        with open(path, 'a') as f:
            f.write(line + '\n')
            f.flush()
        return True
    except Exception:
        return False
    finally:
        safe_umount()


def file_browser_handler(ctx):
    """Interactive, device-aware file browser.
    ctx must contain fb, show, km, base, shift, W, H
    """
    fb = ctx['fb']; show = ctx['show']; km = ctx['km']
    base = ctx['base']; shift = ctx['shift']
    W = ctx.get('W', 320); H = ctx.get('H', 240)

    files = list_files('/sd')
    idx = 0
    scroll = 0

    def draw():
        fb.fill(0)
        fb.text('/sd', 8, 4, 1)
        if not files:
            fb.text('(no files)', 8, 24, 1); show(); return
        start = max(0, idx - 6)
        end = min(len(files), start + 10)
        y = 24
        for i in range(start, end):
            if i == idx: fb.fill_rect(4, y-2, W-8, 12, 1); fb.text(files[i][:40], 8, y, 0)
            else: fb.text(files[i][:40], 8, y, 1)
            y += 12
        fb.text('2/8 move  = open  DEL delete  C back', 8, H-12, 1)
        show()

    def view_file(path):
        # show file contents paginated
        try:
            if not safe_mount():
                return
            with open('/sd/' + path) as f:
                lines = f.read().splitlines()
        except Exception:
            lines = ['<error opening file>']
        finally:
            safe_umount()
        pos = 0
        while True:
            fb.fill(0); fb.text(path, 8, 4, 1)
            y = 24
            page = lines[pos:pos+12]
            for ln in page:
                fb.text(ln[:40], 8, y, 1); y += 12
            fb.text('2/8 scroll  C back', 8, H-12, 1)
            show()
            evs = km.get_events()
            for k, kind in evs:
                if kind != 'tap': continue
                lbl = (shift if False else base).get(k)
                if not lbl: continue
                if lbl == '2' and pos > 0: pos -= 1
                if lbl == '8': pos = min(max(0, len(lines)-12), pos+1)
                if lbl == 'C': return
            time.sleep(0.05)

    # main browser loop
    draw()
    while True:
        evs = km.get_events()
        if not evs:
            time.sleep(0.05); continue
        for k, kind in evs:
            if kind != 'tap': continue
            lbl = (shift if False else base).get(k)
            if not lbl: continue
            if lbl == '2':
                if files: idx = (idx - 1) % len(files); draw()
            elif lbl == '8':
                if files: idx = (idx + 1) % len(files); draw()
            elif lbl == '=' and files:
                view_file(files[idx]); draw()
            elif lbl == 'DEL' and files:
                # confirm delete: simple two-tap confirmation
                fb.fill(0); fb.text('Delete '+files[idx]+'? = yes, C no', 8, H//2-6, 1); show()
                # wait for confirmation
                conf = False
                while True:
                    ev2 = km.get_events()
                    for k2, kind2 in ev2:
                        if kind2 != 'tap': continue
                        lbl2 = (shift if False else base).get(k2)
                        if lbl2 == '=':
                            conf = True; break
                        if lbl2 == 'C': conf = False; break
                    if ev2:
                        break
                    time.sleep(0.05)
                if conf:
                    ok = delete_file(files[idx])
                    if ok:
                        files = list_files('/sd')
                        idx = min(idx, max(0, len(files)-1))
                    draw()
            elif lbl == 'C':
                return
