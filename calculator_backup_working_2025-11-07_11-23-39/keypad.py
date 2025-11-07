"""Minimal keypad shim to provide the expected input API for `main_launcher.py`.
Tries to import the richer `input` module if present; otherwise provides a dummy
implementation that returns no events so the launcher stays responsive.
"""
try:
    from input import km, base, shift, label_for  # prefer original module if present
except Exception:
    try:
        # fallback: try importing under alternate name
        from input_mod import km, base, shift, label_for
    except Exception:
        # Minimal dummy implementation
        class _DummyKM:
            def get_events(self):
                return []
        km = _DummyKM()
        base = {}
        shift = {}
        def label_for(k, shift_on=False):
            return None
