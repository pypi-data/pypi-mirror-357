#!/usr/bin/env python3
"""
Key Display Tool using prompt-toolkit
Shows the Keys enum value when keys are pressed on the keyboard
"""

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import HSplit, Window  # VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from collections import deque
import datetime

class KeyDisplayApp:
    def __init__(self, max_history=20):
        self.max_history = max_history
        self.key_history = deque(maxlen=max_history)
        self.bindings = KeyBindings()
        self.setup_key_bindings()

    def add_key_event(self, key, description=""):
        """Add a key event to the history"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.key_history.append({
            'timestamp': timestamp,
            'key': str(key),
            'description': description
        })

    def setup_key_bindings(self):
        """Set up key bindings to capture all key presses"""

        # Exit on Ctrl+C or Ctrl+Q
        @self.bindings.add('c-c')
        @self.bindings.add('c-q')
        def exit_app(event):
            self.add_key_event(event.key_sequence[0], "Exit application")
            event.app.exit()

        # Special handling for common keys with descriptions
        key_descriptions = {
            Keys.Enter: "Enter/Return key",
            # Keys.Space: "Spacebar",  # spacebar is a printable character
            Keys.Tab: "Tab key",
            Keys.Backspace: "Backspace",
            Keys.Delete: "Delete key",
            Keys.Escape: "Escape key",
            Keys.Up: "Up arrow",
            Keys.Down: "Down arrow",
            Keys.Left: "Left arrow",
            Keys.Right: "Right arrow",
            Keys.Home: "Home key",
            Keys.End: "End key",
            Keys.PageUp: "Page Up",
            Keys.PageDown: "Page Down",
            Keys.Insert: "Insert key",
            Keys.F1: "F1 function key",
            Keys.F2: "F2 function key",
            Keys.F3: "F3 function key",
            Keys.F4: "F4 function key",
            Keys.F5: "F5 function key",
            Keys.F6: "F6 function key",
            Keys.F7: "F7 function key",
            Keys.F8: "F8 function key",
            Keys.F9: "F9 function key",
            Keys.F10: "F10 function key",
            Keys.F11: "F11 function key",
            Keys.F12: "F12 function key",
        }

        # Add specific bindings for described keys
        for key, description in key_descriptions.items():
            self.bindings.add(key)(self.create_key_handler(key, description))

        # Catch-all for any other key
        @self.bindings.add('<any>')
        def handle_any_key(event):
            key = event.key_sequence[0]
            skey = str(key)

            # Skip if already handled by specific binding
            if skey in key_descriptions:
                return

            # Add description for modifier combinations
            description = ""
            if skey.startswith('c-'):
                description = f"Ctrl+{skey[2:].upper()}"
            elif skey.startswith('s-'):
                description = f"Shift+{skey[2:].upper()}"
            elif skey.startswith('m-'):
                description = f"Alt+{skey[2:].upper()}"
            elif len(skey) == 1 and skey.isprintable():
                description = f"Character '{key}'"
            else:
                description = "Special key"

            self.add_key_event(key, description)

    def create_key_handler(self, key, description):
        """Create a key handler function for a specific key"""
        def handler(event):
            self.add_key_event(key, description)
        return handler

    def get_display_content(self):
        """Generate the formatted text content for display"""
        content = []

        # Header
        content.extend([
            ('class:title', '═══ Key Display Tool ═══\n'),
            ('class:subtitle', 'Press any key to see its Keys enum value\n'),
            ('class:instruction', 'Press Ctrl+C or Ctrl+Q to exit\n\n'),
            ('class:header', f'Key History (last {len(self.key_history)} keys):\n'),
            ('class:separator', '─' * 60 + '\n'),
        ])

        # Key history
        if not self.key_history:
            content.append(('class:empty', 'No keys pressed yet...\n'))
        else:
            for entry in reversed(list(self.key_history)):
                timestamp = entry['timestamp']
                key = entry['key']
                description = entry['description']

                content.extend([
                    ('class:timestamp', f'[{timestamp}] '),
                    ('class:key', f'Keys.{key:<15} '),
                    ('class:description', f'({description})\n')
                ])

        return FormattedText(content)

    def create_layout(self):
        """Create the application layout"""
        return Layout(
            HSplit([
                Window(
                    content=FormattedTextControl(
                        text=self.get_display_content,
                        focusable=True
                    ),
                    wrap_lines=True,
                )
            ])
        )

    def create_style(self):
        """Create the application style"""
        return Style.from_dict({
            'title': '#00aa00 bold',
            'subtitle': '#0066cc',
            'instruction': '#888888 italic',
            'header': '#aa6600 bold',
            'separator': '#444444',
            'timestamp': '#666666',
            'key': '#00aa00 bold',
            'description': '#0088cc',
            'empty': '#888888 italic',
        })

    def run(self):
        """Run the key display application"""
        app = Application(
            layout=self.create_layout(),
            key_bindings=self.bindings,
            style=self.create_style(),
            full_screen=True,
            refresh_interval=0.1,  # Refresh 10 times per second
        )

        print("Starting Key Display Tool...")
        print("Press any key to see its Keys enum value")
        print("Press Ctrl+C or Ctrl+Q to exit")

        try:
            app.run()
        except KeyboardInterrupt:
            print("\nExiting...")


def main():
    """Main function to run the key display tool"""
    try:
        app = KeyDisplayApp(max_history=50)
        app.run()
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install prompt-toolkit:")
        print("pip install prompt-toolkit")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

# Additional utility functions for testing specific keys


def test_all_keys():
    """Print all available Keys enum values"""
    print("Available Keys enum values:")
    print("=" * 40)

    # Get all Keys attributes
    keys_attrs = [attr for attr in dir(Keys) if not attr.startswith('_')]

    for i, key_name in enumerate(sorted(keys_attrs), 1):
        key_value = getattr(Keys, key_name)
        print(f"{i:2d}. Keys.{key_name:<20} = {repr(key_value)}")

    print(f"\nTotal: {len(keys_attrs)} key definitions")


def print_key_info(key):
    """Print information about a specific key"""
    print(f"Key: {key}")
    print(f"Type: {type(key)}")
    print(f"String representation: {repr(key)}")
    if hasattr(key, '__dict__'):
        print(f"Attributes: {key.__dict__}")


# Example usage of utility functions
if __name__ == "__main__" and len(__import__('sys').argv) > 1:
    if __import__('sys').argv[1] == "--test-keys":
        test_all_keys()
    else:
        main()
