import re
import time
import colorama
from pathlib import Path
from datetime import datetime as dt

colorama.init(autoreset=True)

root_dir = Path(__file__).absolute().parents[0]
log_dir = root_dir / Path("logs")

# Color constants
reset = colorama.Fore.RESET
debug = colorama.Fore.WHITE
info = colorama.Fore.LIGHTBLACK_EX
warning = colorama.Fore.LIGHTYELLOW_EX
critical = colorama.Fore.LIGHTRED_EX

conversion_table = {
    debug: "DEBUG",
    info: "INFO",
    warning: "WARNING",
    critical: "CRITICAL"
}

def get_date():
    return dt.fromtimestamp(time.time()).strftime("%Y-%m-%d")


class Logger():
    def __init__(self, format_str: str, output_directory=f".", filename=f"{get_date()}.txt",
                 enabled=True, name="ROOT", mode="c", file_compatibility=True,
                 color_enabled=True, open_mode="a+", make_parents=True):

        # Create the file to log messages to.
        self.format_str = format_str
        self.name = name
        self.enabled = enabled
        self.mode = mode
        self.file_compatibility = file_compatibility
        self.color_enabled = color_enabled


        # Logfile & Directory creation
        dir_path = Path(output_directory).absolute()
        file_path = dir_path / Path(filename)
        self.logfile_path = file_path

        # If the file's name is valid (it isn't entirely whitespace)
        if not re.match("[^\s*]", filename):
            raise NameError("Filenames cannot start with whitespace!")

        if not dir_path.exists():
            dir_path.mkdir(parents=make_parents)

        if file_path.exists():
            self.log_file = open(file_path, open_mode)
        else:
            self.log_file = open(file_path, "x+")

        # Append a new line to seperate log sessions if it's not empty.
        with open(file_path, "a") as nl_file:
            nl_file.write("\n")

    def format_message(self, level: str, message: str) -> str:
        """Creates a formatted message using format_str.

        :param message: the message to format.
        :type message: str
        :param level: the level of the message
        :type level: str
        :return: the formatted message
        :rtype: str

        Availible specifiers:
            %D - The current date.
            %T - The current time.
            %N - The logger's name.
            %L - The message's level.
            %% - An escaped percent sign.
        """

        specifiers = {
            "%D": lambda: dt.fromtimestamp(time.time()).strftime("%Y-%m-%d"),
            "%T": lambda: dt.fromtimestamp(time.time()).strftime("%H:%M:%S"),
            "%N": lambda: self.name,
            "%L": lambda: level,
            "%%": lambda: "%"
        }

        formatted = "".join(message)

        for specifier, repl in specifiers.items():
            formatted = formatted.replace(specifier, repl())

        return formatted

    def output_mode(self, message_type: str, output_message: str):
        """Goes through the format mode and outputs it to the output specifier.

        :param message_type: the color from colorama to use
        :type message_type: str
        :param output_message: the message to send to the console or logfile.
        :type output_message: str
        
        Output specifiers:
           c  - Output to the console
           f  - Output to the log file.
           cf - Output to the console AND log file.
        """

        for specifier in self.mode:
            # Console specifier
            if specifier == "c":
                if self.color_enabled:
                    print(message_type + output_message)
                else:
                    print(output_message)

            # Logfile specifier. If log_file is None, there is no file to log
            # the output to.
            if specifier == "f" and self.log_file is not None:
                # Wont send color information to the logfile.
                if self.file_compatibility:
                    self.log_file.write(output_message + "\n")
                # Will send color information to the logfile.
                else:
                    self.log_file.write(message_type + output_message + reset + "\n")

    def debug(self, debug_message: str):
        """Sends text to the console, or file with white text.

        :param debug_message: the debug message
        :type debug_message: str
        """

        if not self.enabled:
            return 

        formatted_debug: str = self.format_message("DEBUG", self.format_str) \
                             + " " + self.format_message("DEBUG", debug_message)

        self.output_mode(debug, formatted_debug)

    def info(self, info_message: str):
        """Sends text to the console, or file with grey text.

        :param info: the info message
        :type info: str
        """

        if not self.enabled:
            return

        formatted_info: str = self.format_message("INFO", self.format_str) \
                            + " " + self.format_message("INFO", info_message)

        self.output_mode(info, formatted_info)

    def warn(self, warning_message: str):
        """Sends text to the console, or file with yellow text.

        :param warning_message: the warning message
        :type warning_message: str
        """

        if not self.enabled:
            return 

        formatted_warning: str = self.format_message("WARNING", self.format_str) \
                               + " " + self.format_message("WARNING", warning_message)

        self.output_mode(warning, formatted_warning)
       
    def critical(self, critical_message: str):
        """Sends text to the console, or file with red text.

        :param critical_message: the critical_message
        :type critical_message: str
        """

        if not self.enabled:
            return 

        formatted_critical: str = self.format_message("CRITICAL", self.format_str) \
                                + " " + self.format_message("CRITICAL", critical_message)

        self.output_mode(critical, formatted_critical)
