"""
Simple calculator REPL for the Pico basic mode.

Features:
- Serial REPL input (works on the device over USB serial).
- Safe evaluation using a restricted namespace (common math functions only).
- Optional display of expression/result if `drivers.ili9341` is available.

This is intentionally small and self-contained so it can run on MicroPython.
"""
import time
try:
    from drivers.ili9341 import ILI9341
except Exception:
    ILI9341 = None
try:
    import math as _math
except Exception:
    _math = None

def _build_allowed_namespace():
    ns = {}
    if _math:
        for n in ('sin','cos','tan','asin','acos','atan','sqrt','log','log10','exp','pow','pi','e','floor','ceil'):
            if hasattr(_math, n):
                ns[n] = getattr(_math, n)
    # basic builtins we allow
    ns.update({'abs': abs, 'round': round, 'pow': pow, 'min': min, 'max': max})
    return ns

ALLOWED = _build_allowed_namespace()

def safe_eval(expr: str):
    """Evaluate arithmetic expression safely using restricted globals.

    This function rejects obviously dangerous tokens and uses eval with
    an empty __builtins__ and a small allowlist of names.
    """
    e = expr.strip()
    # Quick rejects
    bad = ('__', 'import', 'open', 'exec', 'eval', 'os.', 'sys.', 'subprocess', 'socket')
    for b in bad:
        if b in e:
            raise ValueError('unsafe token in expression')
    try:
        # Use eval with no builtins and our allowed names
        return eval(e, {'__builtins__': None}, ALLOWED)
    except Exception as ex:
        raise

def _display_lines(lines):
    if ILI9341 is None:
        return
    try:
        disp = ILI9341()
        try:
            disp.init_display()
        except Exception:
            pass
        # Many ILI9341 wrappers expose a `text` helper; if not, skip gracefully
        y = 0
        color = 0xFFFF
        for ln in lines:
            try:
                disp.text(str(ln), 2, y, color)
            except Exception:
                # fallback: try drawing a small rectangle or ignore
                pass
            y += 12
    except Exception:
        pass

def main():
    print('🧮 Simple Basic Calculator')
    print('Type expressions like: 2+2, (3+4)/2, sin(3.14/2)')
    print('Commands: exit, quit, help')
    if ILI9341:
        _display_lines(['Simple Calc', 'Type expression', 'over serial'])
    while True:
        try:
            expr = input('> ')
        except (EOFError, KeyboardInterrupt):
            print('\nExiting simple calculator')
            break
        if expr is None:
            continue
        s = expr.strip()
        if not s:
            continue
        if s.lower() in ('exit', 'quit'):
            print('Bye')
            break
        if s.lower() in ('help', '?'):
            print('Enter a math expression. Allowed functions: ' + ', '.join(sorted(ALLOWED.keys())))
            continue
        try:
            res = safe_eval(s)
            print('= {}'.format(res))
            if ILI9341:
                _display_lines([s, '=', str(res)])
        except Exception as e:
            print('Error:', e)
