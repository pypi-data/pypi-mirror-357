import sys
import os

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import tty

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    REVERSE = "\033[7m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"

def enable_windows_ansi():
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class CliMenu:
    def __init__(self, options, title=None, description=None, multiselect=False,
                 page_size=10, color=True, exit_keys=None, callbacks=None):
        self.options = options
        self.title = title
        self.description = description
        self.multiselect = multiselect
        self.page_size = page_size
        self.color = color and (os.name != 'nt' or 'ANSICON' in os.environ or 'WT_SESSION' in os.environ)
        self.exit_keys = exit_keys or ['q', '\x1b']
        self.callbacks = callbacks or {}

        self.selected = 0
        self.selected_multiple = set()
        self.page = 0
        self.pages_count = max(1, (len(self.options) + page_size - 1) // page_size)

        if self.color:
            enable_windows_ansi()

    def _getch(self):
        if os.name == 'nt':
            ch = msvcrt.getch()
            if ch in (b'\xe0', b'\x00'):
                ch2 = msvcrt.getch()
                return ch + ch2
            return ch
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch += sys.stdin.read(2)
                return ch.encode()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _color_text(self, text, color_code):
        if not self.color:
            return text
        return f"{color_code}{text}{Colors.RESET}"

    def _print_title_desc(self):
        if self.title:
            print(self._color_text(self.title, Colors.BOLD + Colors.FG_CYAN))
        if self.description:
            print(self.description)
        if self.title or self.description:
            print()

    def _print_options(self):
        start = self.page * self.page_size
        end = min(start + self.page_size, len(self.options))
        for i in range(start, end):
            prefix = "=> " if i == self.selected else "   "
            option_text = self.options[i]
            if self.multiselect:
                mark = "[x]" if i in self.selected_multiple else "[ ]"
                option_text = f"{mark} {option_text}"

            if i == self.selected:
                option_text = self._color_text(option_text, Colors.REVERSE)

            print(f"{prefix}{option_text}")

        if self.pages_count > 1:
            print()
            print(f"Page {self.page + 1}/{self.pages_count} (Left/Right arrow keys to navigate pages)")

    def show(self):
        while True:
            self._clear()
            self._print_title_desc()
            self._print_options()

            key = self._getch()

            if os.name == 'nt':
                if key == b'\xe0H':  # haut
                    self.selected = (self.selected - 1) % len(self.options)
                    if self.selected < self.page * self.page_size:
                        self.page = max(0, self.page - 1)
                elif key == b'\xe0P':  # bas
                    self.selected = (self.selected + 1) % len(self.options)
                    if self.selected >= (self.page + 1) * self.page_size:
                        self.page = min(self.pages_count - 1, self.page + 1)
                elif key == b'\xe0K':  # gauche
                    self.page = max(0, self.page - 1)
                    self.selected = self.page * self.page_size
                elif key == b'\xe0M':  # droite
                    self.page = min(self.pages_count - 1, self.page + 1)
                    self.selected = self.page * self.page_size
                elif key == b' ':  # espace
                    if self.multiselect:
                        if self.selected in self.selected_multiple:
                            self.selected_multiple.remove(self.selected)
                        else:
                            self.selected_multiple.add(self.selected)
                elif key == b'\r':  # entrée
                    if self.multiselect:
                        return sorted(self.selected_multiple)
                    else:
                        if self.selected in self.callbacks:
                            self.callbacks[self.selected]()
                        return self.selected
                else:
                    if key.decode().lower() in self.exit_keys:
                        return None

            else:
                if key == b'\x1b[A':  # haut
                    self.selected = (self.selected - 1) % len(self.options)
                    if self.selected < self.page * self.page_size:
                        self.page = max(0, self.page - 1)
                elif key == b'\x1b[B':  # bas
                    self.selected = (self.selected + 1) % len(self.options)
                    if self.selected >= (self.page + 1) * self.page_size:
                        self.page = min(self.pages_count - 1, self.page + 1)
                elif key == b'\x1b[D':  # gauche
                    self.page = max(0, self.page - 1)
                    self.selected = self.page * self.page_size
                elif key == b'\x1b[C':  # droite
                    self.page = min(self.pages_count - 1, self.page + 1)
                    self.selected = self.page * self.page_size
                elif key == b' ':  # espace
                    if self.multiselect:
                        if self.selected in self.selected_multiple:
                            self.selected_multiple.remove(self.selected)
                        else:
                            self.selected_multiple.add(self.selected)
                elif key == b'\r':  # entrée
                    if self.multiselect:
                        return sorted(self.selected_multiple)
                    else:
                        if self.selected in self.callbacks:
                            self.callbacks[self.selected]()
                        return self.selected
                else:
                    try:
                        if key.decode().lower() in self.exit_keys:
                            return None
                    except:
                        pass
