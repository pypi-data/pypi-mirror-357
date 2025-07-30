from collections import abc
from datetime import datetime
import json
import logging
from pathlib import Path
from pyquest.constants import LOG_PATH
import sys
import threading
import itertools
import time
from pyquest.constants import text_colors, token_colors


def cprint(*args):
    """
    Print text in color. Supports either a single color and text or a list of color-text pairs.

    Args:
         A single color and text or a list of color-text pairs.
         For example: cprint('red', 'Hello') or cprint(['red', 'Hello', 'green', 'World'])
    """
    if isinstance(args[0], list):
        args = args[0]
    # Iterate over the arguments in pairs of color and text
    for i in range(0, len(args), 2):
        print(f"{text_colors[args[i]]}{args[i + 1]}{text_colors['reset']}", end=" ")
    print()  # Print a newline at the end


def status_lights(status_colors: list[str]):
    """
    Create status lights (circles) in color.

    Args:
        status_colors: A list of status colors (e.g. ['red', 'green', 'yellow']).

    Returns:
        A string representation of colored status lights.
    """
    circle = "●"  # Unicode character for a filled circle
    return "".join(f"{text_colors[color]}{circle}{text_colors['reset']}" for color in status_colors)


class Spinner:
    def __init__(self, color, message="Loading..."):
        """
        Initialize the Spinner object.

        Args:
            color: The color of the spinner.
            message: The message to display beside the spinner.
        """
        self.done = False
        self.message = message
        self.color = color
        self.thread = threading.Thread(target=self.spin)

    def _write(self, text):
        """Write text to stdout and flush."""
        sys.stdout.write(text)
        sys.stdout.flush()

    def _hide_cursor(self):
        """Hide the terminal cursor."""
        self._write("\033[?25l")

    def _show_cursor(self):
        """Show the terminal cursor."""
        self._write("\n\033[?25h")

    def spin(self):
        """Display a multi-spinner animation until stopped."""
        frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # Frames used for each spinner
        done_frame = "⠿⠿⠿⠿"  # Frames to show on completion

        # Create four separate cycle iterators for the spinners
        spinners = [itertools.cycle(frames) for _ in range(4)]

        # Initialize each spinner with staggered positions for visual effect
        for i, spinner in enumerate(spinners):
            for _ in range(i * 2):  # Stagger each spinner by 2 frames
                next(spinner)

        self._hide_cursor()
        while not self.done:
            # Construct the spinner display from each staggered spinner
            spinner_display = "".join(next(spinner) for spinner in spinners)
            self._write(f"\r{text_colors[self.color]}{self.message} {text_colors['darkyellow']}{spinner_display}")
            time.sleep(0.1)  # Control the speed of spinner animation

        # Display the "done" frame when completed
        self._write(f"\r{text_colors[self.color]}{self.message} {text_colors['lightgreen']}{done_frame}")
        self._show_cursor()

    def start(self):
        """Start the spinner in a separate thread."""
        self.thread.start()

    def stop(self):
        """Stop the spinner and wait for the thread to finish."""
        self.done = True
        self.thread.join()  # Ensure the spinner thread is fully stopped


log = logging.getLogger()


def is_serializable_type(obj):

    return (
        obj.__class__.__module__ == '__builtin__'
        or obj is None
    )


def dictify(obj, ignore_class_names=('Session',), ignore_startswith='_', ignore_endswith='_'):
    """ Recursively convert lists and dicts to built-in types serializable by json.dumps() """
    if callable(getattr(obj, 'isoformat', None)):
        return obj.isoformat()
    if isinstance(obj, abc.Mapping):
        return {k: dictify(v) for k, v in obj.items() if not (
            k.startswith(ignore_startswith) or k.endswith(ignore_endswith) or v.__class__.__name__ in ignore_class_names
        )}
    if isinstance(obj, (list, tuple)) or callable(getattr(obj, '__iter__', None)):
        return [dictify(x) for x in obj]
    if isinstance(obj, bytes):
        return obj.decode()
    try:
        obj = float(obj)
        if obj == int(obj):
            obj = int(obj)
    except (TypeError, ValueError) as err:
        log.debug(f'{obj} cannot be converted to an int or float: {err}')

    # `Mapping`s do NOT have a `__dict__` attr, so this check is redundant with above `if`
    if is_serializable_type(obj):
        # FIXME: deal with non-builtin without a __dict__ attr using str() or repr()
        return obj
    if not hasattr(obj, '__dict__'):
        return str(obj)
    d = dict()
    for k, v in vars(obj).items():
        if k.startswith(ignore_startswith) or k.endswith(ignore_endswith) or v.__class__.__name__ in ignore_class_names:
            continue
        d[k] = dictify(v)
    return d


class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format"""

    def format(self, record):
        # Create the log entry dictionary
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'pathname': record.pathname,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        extra_data = dictify(getattr(record, 'extra_data', None) or {})
        if isinstance(extra_data, dict):
            log_entry.update(extra_data)
        else:
            log_entry.update(dict(extra_data=extra_data))

        return json.dumps(log_entry, ensure_ascii=False)


class ModuleLineFormatter(logging.Formatter):
    """Custom formatter for stderr with module and line info"""

    def format(self, record):
        # Format: [LEVEL] module:line - message
        return f"[{record.levelname}] {record.module}:{record.lineno} - {record.getMessage()}"


def setup_logging(
    name=__name__,
    log_file=LOG_PATH,
    log_level=logging.INFO,
    file_log_level=logging.DEBUG,
    stderr_log_level=logging.INFO


):
    """
    Set up logging with JSON format to file and module:line format to stderr

    Args:
        log_file: Path to the log file
        log_level: Overall logging level
        file_log_level: Logging level for file handler
        stderr_log_level: Logging level for stderr handler
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File handler with JSON formatting
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(JSONFormatter())

    # Stderr handler with module:line formatting
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(stderr_log_level)
    stderr_handler.setFormatter(ModuleLineFormatter())

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stderr_handler)

    return logger


def test_logger(log_path=LOG_PATH.with_suffix('.log.test')):
    """ Example usage and logger tests """
    logger = setup_logging(
        name=__name__,
        log_file=log_path,
        log_level=logging.DEBUG,
        file_log_level=logging.DEBUG,
        stderr_log_level=logging.INFO
    )

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("Application started successfully")
    logger.warning("This is a warning message")
    logger.error("An error occurred")

    # Test logging with extra data (for JSON)
    logger.info("User action", extra={'extra_data': {
        'user_id': 12345,
        'action': 'login',
        'ip_address': '192.168.1.1'
    }})

    # Test exception logging
    try:
        result = 1 / 0  # noqa
    except ZeroDivisionError:
        logger.exception("Intentional divide-by-zero error occurred")

    # Example of getting a named logger for a specific module
    module_logger = logging.getLogger(__name__)
    module_logger.info("This message includes the module name")

    print("\nLogging tests complete!")
    print(f"Check the '{log_path}' file for JSON formatted logs")
    print("Check stderr output above for module:line formatted logs")


def get_module_logger(name=None):
    """Get a logger for a specific module"""
    if name is None:
        name = __name__
    return logging.getLogger(name)
