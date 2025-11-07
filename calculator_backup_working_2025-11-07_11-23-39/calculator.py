"""
calculator.py

Safe calculator evaluator and a device-aware handler to integrate with ModeMenu.

Handler signature: calc_handler(ctx)
  ctx should contain at minimum:
    - 'fb' : framebuf.FrameBuffer (device)
    - 'show': callable to flush framebuffer to display
    - 'km' : input.km (Keys instance)
    - 'base', 'shift' : key maps

On host (no 'fb' in ctx) the handler will run a simple console loop for testing.
"""

import math
import time

SAFE_GLOBALS = {"__builtins__": None, "math": math}
MAX_EXPR_LEN = 128

def preprocess(e):
    if not e: return e
    e = e.replace('√', 'math.sqrt').replace('π', str(math.pi))
    e = e.replace('^2','**2')
    e = e.replace('^', '**')
    for fn in ['sin','cos','tan','asin','acos','atan','exp','sqrt','log','log10','log2','floor','ceil','abs']:
        e = e.replace(fn+'(', 'math.'+fn+'(')
    e = e.replace('ln(', 'math.log(')
    e = e.replace('log(', 'math.log10(')
    e = e.replace('÷', '/')
    return e

def evaluate_live(s):
    if not s: return ""
    try:
        val = eval(preprocess(s), SAFE_GLOBALS, {})
        if isinstance(val, float):
            if math.isfinite(val): return '{:.10g}'.format(val)
            return 'Error'
        return str(val)
    except Exception:
        return ""

def evaluate_final(s):
    if not s: return 'Error'
    try:
        val = eval(preprocess(s), SAFE_GLOBALS, {})
        if isinstance(val, float):
            if not math.isfinite(val): return 'Error'
            return '{:.10g}'.format(val)
        return str(val)
    except Exception as e:
        return 'Error'


def _draw_fb(fb, show, W, H, expr, out, shift_on):
    bg = 0
    fg = 1
    fb.fill(bg)
    # simple layout
    inp = expr if len(expr) <= 38 else '...' + expr[-35:]
    fb.text('In: ' + inp, 8, 16, fg)
    live = evaluate_live(expr) if expr else ''
    fb.text('Out: ' + (live if live != '' else out), 8, 36, fg)
    fb.text('S:Shift ' + ('ON' if shift_on else 'OFF'), 8, H-16, fg)
    show()


def calc_handler(ctx):
    """Device-aware calculator handler.
    ctx: dict with keys 'fb','show','km','base','shift'
    """
    # Host console fallback
    if 'fb' not in ctx or 'show' not in ctx:
        print('[calc] Running in console mode. Type expressions or C to exit.')
        expr = ''
        out = ''
        while True:
            cmd = input('expr> ').strip()
            if cmd.upper() == 'C':
                print('Exit calc')
                return
            if cmd == '':
                continue
            if cmd == '=':
                out = evaluate_final(expr)
                print('=>', out)
                continue
            expr = cmd
            print('live =>', evaluate_live(expr) or out)

    fb = ctx['fb']; show = ctx['show']; km = ctx['km']
    base = ctx['base']; shift = ctx['shift']
    W = ctx.get('W', 320); H = ctx.get('H', 240)

    expr = ''; out = ''
    shift_on = False

    # draw initial
    _draw_fb(fb, show, W, H, expr, out, shift_on)

    while True:
        events = km.get_events()
        for (k, kind) in events:
            lbl = (shift if shift_on else base).get(k)
            if not lbl: continue
            if lbl == 'S' and kind == 'tap':
                shift_on = not shift_on
                _draw_fb(fb, show, W, H, expr, out, shift_on)
                continue
            if lbl == '=' and kind == 'tap':
                out = evaluate_final(expr)
                _draw_fb(fb, show, W, H, expr, out, shift_on)
                continue
            if lbl == 'DEL' and kind == 'tap':
                if expr: expr = expr[:-1]; _draw_fb(fb, show, W, H, expr, out, shift_on); continue
            if lbl == 'C' and kind == 'tap':
                return
            if kind == 'tap':
                if len(expr) >= MAX_EXPR_LEN: _draw_fb(fb, show, W, H, expr, out, shift_on); continue
                if lbl == '^2': expr += '**2'
                elif lbl == '√': expr += 'math.sqrt('
                elif lbl == '/': expr += '/'
                else: expr += lbl
                _draw_fb(fb, show, W, H, expr, out, shift_on)
        # small sleep to avoid busy loop
        time.sleep(0.02)
