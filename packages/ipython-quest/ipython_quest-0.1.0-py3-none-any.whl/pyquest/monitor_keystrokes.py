""" 3. Comprehensive Monitoring System """
from collections import deque
from IPython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic
from pyquest.monitor_prompt_toolkit import KeystrokeMonitor
import statistics


ip, monitor = None, None


@magics_class
class LearningAnalytics(Magics):

    def __init__(self, shell=None):
        global ip, monitor
        super().__init__(shell=shell)
        self.keystroke_times = deque(maxlen=100)
        self.typing_patterns = []
        self.paste_events = []
        monitor = KeystrokeMonitor()

    def analyze_typing_pattern(self, keystrokes):
        """Analyze if keystroke pattern suggests natural typing vs pasting"""
        if len(keystrokes) < 5:
            return "insufficient_data"

        intervals = [ks['time_delta'] for ks in keystrokes if ks['time_delta'] > 0]

        if not intervals:
            return "no_intervals"

        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

        # Natural typing: 0.1-0.3s between keystrokes, some variation
        # Pasting: Very fast, uniform intervals
        if avg_interval < 0.05 and std_interval < 0.02:
            return "likely_paste"
        elif avg_interval > 0.5:
            return "slow_typing"
        else:
            return "natural_typing"

    @line_magic
    def typing_stats(self, line):
        """Show typing statistics"""
        if hasattr(monitor, 'keystrokes') and monitor.keystrokes:
            pattern = self.analyze_typing_pattern(monitor.keystrokes[-20:])
            print(f"Recent typing pattern: {pattern}")
            print(f"Total keystrokes monitored: {len(monitor.keystrokes)}")
            if monitor.keystrokes:
                recent_speed = statistics.mean([ks['time_delta']
                                                for ks in monitor.keystrokes[-10:]
                                                if ks['time_delta'] > 0])
                print(f"Average keystroke interval: {recent_speed:.3f}s")
        else:
            print("No keystroke data available")

    @line_magic
    def reset_monitoring(self, line):
        """Reset keystroke monitoring"""
        if 'monitor' in globals():
            monitor.keystrokes.clear()
            print("Keystroke monitoring reset")


if __name__ == '__main__':
    # Register magic commands
    ip = get_ipython()
    ip.register_magic_function(LearningAnalytics(ip).typing_stats)
    ip.register_magic_function(LearningAnalytics(ip).reset_monitoring)
