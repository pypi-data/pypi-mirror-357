""" 1. Prompt Toolkit KeyBindings (Claude recommendation) """
from IPython import get_ipython
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings
from prompt_toolkit.keys import Keys
import string
import time


class KeystrokeMonitor:
    def __init__(self):
        self.keystrokes = []
        self.last_keystroke_time = 0
        self.typing_speed_threshold = 0.05  # seconds between keystrokes
        self.paste_detection_count = 10  # chars in quick succession = paste

    def log_keystroke(self, key, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        self.keystrokes.append((
            timestamp,
            timestamp - self.last_keystroke_time,
            key,
        ))

        self.last_keystroke_time = timestamp
        self.detect_paste_behavior()

    def detect_paste_behavior(self):
        if len(self.keystrokes) < self.paste_detection_count:
            return

        # Check last N keystrokes for rapid input
        recent_keystrokes = self.keystrokes[-self.paste_detection_count:]
        rapid_inputs = sum(1 for ks in recent_keystrokes
                           if ks[1] < self.typing_speed_threshold)

        if rapid_inputs >= self.paste_detection_count - 2:
            print("\n🚨 PASTE DETECTED: Consider typing the code yourself for better learning!")
            self.keystrokes.clear()  # Reset to avoid repeated warnings


ip, monitor = None, None


def monitor_prompt_toolkit():
    global ip, monitor
    monitor = KeystrokeMonitor()
    ip = get_ipython()
    if not hasattr(ip, 'pt_app') or ip.pt_app is None:
        print("Prompt toolkit not available")
        return

    # Get existing key bindings
    existing_bindings = ip.pt_app.key_bindings

    # Create new bindings that wrap existing ones
    new_bindings = KeyBindings()

    # Monitor all printable characters
    for char in string.printable:
        @new_bindings.add(char)
        def _(event, c=char):
            monitor.log_keystroke(c)
            # Pass through to normal handling
            event.app.current_buffer.insert_text(c)

    @new_bindings.add(Keys.Enter)
    def _(event):
        monitor.log_keystroke('ENTER')
        event.app.current_buffer.validate_and_handle()

    @new_bindings.add(Keys.Backspace)
    def _(event):
        monitor.log_keystroke('BACKSPACE')
        event.app.current_buffer.delete_before_cursor()

    # Detect Ctrl+V paste
    @new_bindings.add(Keys.ControlV)
    def _(event):
        print("\n🚨 PASTE SHORTCUT DETECTED: Try typing the code yourself!")
        monitor.log_keystroke('CTRL+V_PASTE')
        # Still allow the paste to proceed
        event.app.current_buffer.paste_clipboard_data(
            event.app.clipboard.get_data()
        )

    # Merge with existing bindings
    ip.pt_app.key_bindings = merge_key_bindings([existing_bindings, new_bindings])
    return ip, monitor


if __name__ == '__main__':
    ip, monitor = monitor_prompt_toolkit()
