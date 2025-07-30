""" 4. Clipboard Monitoring """
import logging
import threading
import time
try:
    import pyperclip
    clipboard_available = True
except ImportError:
    clipboard_available = False
    print("Install pyperclip for clipboard monitoring: pip install pyperclip")

log = logging.getLogger(__name__)


class ClipboardMonitor:
    def __init__(self):
        self.last_clipboard = ""
        self.monitoring = False

    def start_monitoring(self):
        if not clipboard_available:
            return

        self.monitoring = True
        thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        thread.start()

    def _monitor_clipboard(self):
        while self.monitoring:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != self.last_clipboard and len(current_clipboard) > 10:
                    print(f"\n📋 Clipboard changed - new content: {len(current_clipboard)} chars")
                    if '\n' in current_clipboard:
                        print("⚠️  Multi-line code detected in clipboard")
                    self.last_clipboard = current_clipboard
            except Exception as e:
                log.error(e)
                pass
            time.sleep(1)


if __name__ == '__main__':
    # Start clipboard monitoring
    clipboard_monitor = ClipboardMonitor()
    clipboard_monitor.start_monitoring()
