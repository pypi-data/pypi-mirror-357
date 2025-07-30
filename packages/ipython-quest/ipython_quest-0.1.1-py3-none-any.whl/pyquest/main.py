from IPython import start_ipython
from IPython.terminal.prompts import Prompts
from IPython.terminal.ipapp import load_default_config
from pygments.token import Token
from pyquest.constants import token_colors
from pyquest.util import cprint
from pprint import pprint
import logging
import importlib
import readline  # noqa

shell = None

# FIXME: make this a table with 3 fields/columns in local Sqlite cache and remote Supabase DB
quest = dict(
    status=dict(
        points=0,
        grade='F',
        step_num=0,
    ),
    goal=dict(
        found_help=0,
        ran_help=0,
        found_hidden=[],
    ),
    # Miniquests
    hint=[
        '1: What is the full path to your current working directory - the default place where any files will be saved.',
        '2: What files are in your "current working directory" - the default directory or folder where files will be saved.',
        '3: Find and run the function you use to get help on any function in Python.',
        '4: Find and display the contents of as many hidden iPython variables as you can find.',
    ],
)


def get_hint(step_num=0):
    global quest
    quest['status']['step_num'] = step_num = step_num or quest['status']['step_num']
    return quest['hint'][step_num]


class QuestPrompt(Prompts):
    """ Custom iPython Quest Prompt """
    # def __init__(self, shell):
    # def vi_mode(self): ... return ''
    # def current_line(self) -> int:
    # def in_prompt_tokens(self):
    # def _width(self):
    # def continuation_prompt_tokens(self, width=None, *, lineno=None, wrap_count=None):
    # def rewrite_prompt_tokens(self):
    # def out_prompt_tokens(self):

    def in_prompt_tokens(self, cli=None):
        return [
            (Token.Gray, f">>> # {get_hint()}\n"),
            (Token.Green, ">>> ")]  # + aws_profile_prompt


class Shell:
    """ iPython adventures

    Commands:
      - help: Show this help message
      - docs: Open browser to show Workbench Documentation
      - config: Show the current Config
      - status: Show the current Status
      - log_(debug/info/important/warning): Set the Workbench log level
      - exit: Close the shell session and exit to the parent shell

    """

    def __init__(self):
        # # Check the Workbench config
        # self.cm = ConfigManager()
        # if not self.cm.config_okay():
        #     # Invoke Onboarding Procedure
        #     onboard()

        # Our Metadata Object pull information from the Cloud Platform
        self.meta = None
        self.meta_status = "DIRECT"

        # Perform AWS connection test and other checks
        self.commands = dict(
            #            help=self.help,
            status=self.print_status,
            # quest=self.show_quest,
            log_debug=self.log_debug,
            log_info=self.log_info,
            log_warning=self.log_warning,
            # config=self.show_config,
            log=logging.getLogger('pyquest'),
            # pd=importlib.import_module("pandas"),
            pprint=importlib.import_module("pprint").pprint,
        )

    def start(self):
        """Start the enhanced IPython shell"""
        cprint("magenta", "\nWelcome to the iPython adventure game!")

        # Load the default IPython configuration
        config = load_default_config()
        # # Don't automatically call functions entered without parentheses
        # config.TerminalInteractiveShell.autocall = 2
        config.TerminalInteractiveShell.prompts_class = QuestPrompt
        config.TerminalInteractiveShell.highlighting_style_overrides = token_colors
        config.TerminalInteractiveShell.banner1 = ""

        # Merge custom commands and globals into the namespace
        locs = self.commands.copy()  # Copy the custom commands
        locs.update(globals())  # Merge with global namespace

        # Start IPython with the config and commands in the namespace
        start_ipython(["--no-tip", "--theme", "linux"], user_ns=locs, config=config)

    def show_config(self):
        cprint("yellow", "\nConfig:")
        cprint("lightblue", f"Path: {self.cm.site_config_path}")
        config = self.cm.get_all_config()
        for key, value in config.items():
            cprint(["lightpurple", "\t" + key, "lightgreen", value])

    # def spinner_start(self, text: str, color: str = "lightpurple") -> Spinner:
    #     spinner = Spinner(color, text)
    #     spinner.start()  # Start the spinner
    #     return spinner

    def print_status(self):
        """Show current progress and scores on learning quest"""
        status_data = self.get_status()

        cprint("yellow", "\nStatus:")
        pprint(status_data)
        return status_data

    @staticmethod
    def log_debug():
        logging.getLogger("pyquest").setLevel(logging.DEBUG)

    @staticmethod
    def log_info():
        logging.getLogger("pyquest").setLevel(logging.INFO)

    @staticmethod
    def log_warning():
        logging.getLogger("pyquest").setLevel(logging.WARNING)


def main():
    shell = Shell()
    shell.start()
    return shell


# Start the shell when running the script
if __name__ == "__main__":
    main()
