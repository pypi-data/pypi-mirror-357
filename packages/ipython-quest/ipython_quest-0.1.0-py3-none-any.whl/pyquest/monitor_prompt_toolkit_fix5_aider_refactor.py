""" 1. Prompt Toolkit KeyBindings (Claude recommendation) """
from IPython import get_ipython, start_ipython
import jsonlines
import logging
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings
from prompt_toolkit.keys import Keys
from pyquest.constants import setup_logging
import string
import sys
import time

from pyquest.constants import LOG_PATH

log = logging.getLogger()
logger = setup_logging()

# SPECIAL_KEYS should not be bound
# SPECIAL_KEYS are a subset of {key: name for (name, key) in Keys._member_map_.items()}
SPECIAL_KEYS = {}
for name in 'Enter ControlH ControlM Tab Backspace Delete Escape Up Down Left Right Home End PageUp PageDown Insert'.split():
    SPECIAL_KEYS[getattr(Keys, name)] = f"[{name}]".upper()
for fnum in range(1, 12):
    SPECIAL_KEYS[getattr(Keys, f"F{fnum}")] = f"[F{fnum}]".upper()

del SPECIAL_KEYS[Keys.Enter]
# del SPECIAL_KEYS[Keys.Backspace]


def warn(msg):
    fout = jsonlines.open(LOG_PATH, mode='a')
    fout.write(msg)
    log.warn(msg)
    logger.warn(msg)
    fout.close


class KeyLogger:
    def __init__(self):
        self.keystrokes = []
        self.last_keystroke_time = 0

    def log_keystroke(self, key, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        self.keystrokes.append((
            timestamp,
            timestamp - self.last_keystroke_time,
            key,
        ))
        self.last_keystroke_time = timestamp


class FastKeystrokeMonitor(KeyLogger):
    def __init__(self, *args, typing_speed_threshold=0.1, **kwargs):
        if len(args):
            typing_speed_threshold = args[0]
            args = args[1:]
        self.typing_speed_threshold = typing_speed_threshold  # seconds between keystrokes
        self.fast_typing_count = 10
        super().__init__(*args, **kwargs)

    def log_keystroke(self, key, timestamp=None):
        super().log_keystroke(key=key, timestamp=timestamp)
        if timestamp is None:
            timestamp = time.time()
        self.detect_fast_typing()

    def detect_fast_typing(self):
        if len(self.keystrokes) < self.fast_typing_count:
            return
        recent_keystrokes = self.keystrokes[-self.fast_typing_count:]
        rapid_inputs = sum(1 for ks in recent_keystrokes
                           if ks[1] < self.typing_speed_threshold)
        if rapid_inputs >= self.fast_typing_count - 2:
            log.warning("\n🚨 INHUMAN TYPING!: Consider typing the code a little slower for better learning!")
            self.keystrokes.clear()  # Reset to avoid repeated warnings


class PasteMonitor(KeyLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def log_paste(self, key, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        self.keystrokes.append((
            timestamp,
            "PASTE",
            key,
        ))


ip, monitor = None, None


def monitor_prompt_toolkit(allow_paste=False, allow_fast_typing=False, typing_speed_threshold=0.1):
    global ip, monitor
    if allow_fast_typing:
        monitor = FastKeystrokeMonitor(typing_speed_threshold=typing_speed_threshold)
    else:
        monitor = PasteMonitor()

    ip = get_ipython()
    if ip is None:
        start_ipython()
        ip = get_ipython()
    assert ip is not None
    assert getattr(ip, 'pt_app', None) is not None

    existing_bindings = ip.pt_app.key_bindings
    new_bindings = KeyBindings()
    for char in string.printable:
        @new_bindings.add(char)
        def _(event, c=char):
            monitor.log_keystroke(c)
            event.app.current_buffer.insert_text(c)

    # Monitor common paste hotkeys
    if not allow_paste:
        for k in (Keys.ControlV, Keys.Insert, Keys.ControlInsert, Keys.ShiftInsert, Keys.ControlShiftInsert, Keys.BracketedPaste):
            @new_bindings.add(k)
            def _monitor_paste(event):
                print("\n🚨 PASTE BLOCKED: Try typing the code yourself!")
                monitor.log_paste(f'{str(k)}(PASTE?)')
                # event.app.current_buffer.validate_and_handle()

    # Merge with existing bindings
    ip.pt_app.key_bindings = merge_key_bindings([existing_bindings, new_bindings])
    return ip, monitor


if __name__ == '__main__':
    typing_speed_threshold = 0.03
    if len(sys.argv[1:]):
        typing_speed_threshold = float(sys.argv[1])
    allow_paste = False
    if len(sys.argv[2:]):
        allow_paste = bool(eval(sys.argv[2]))
    print(allow_paste, typing_speed_threshold)
    ip, monitor = monitor_prompt_toolkit(allow_paste=allow_paste, typing_speed_threshold=typing_speed_threshold)
