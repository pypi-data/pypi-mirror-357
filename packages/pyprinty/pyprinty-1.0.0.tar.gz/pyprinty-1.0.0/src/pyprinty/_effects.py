class Effects:
    Bold          = "\033[1m"
    Dim           = "\033[2m"
    Italic        = "\033[3m"
    Underline     = "\033[4m"
    Dubleline     = "\033[21m"
    Blink         = "\033[5m"
    Speedblink    = "\033[6m"
    Strikethrough = "\033[9m"
    Upline        = "\033[53m"
    CLEAR_EFFECTS = "\033[0m"


class Cursor:
    JUMP = lambda x, y: f"\033[{y};{x}H"
    RIGHT = lambda num: f"\033[{num}C"
    DOWN = lambda num: f"\033[{num}B"
    LEFT = lambda num: f"\033[{num}D"
    UP = lambda num: f"\033[{num}F"
    CLEAR_LINE = "\033[2K\r"
    CLEAR_ALL = "\033c"
    HIDE = "\033[?25l"
    SHOW = "\033[?25h"
    SAVE = "\x1b[s"
    BACK = "\x1b[u"
    PRINT = lambda name: print(name, end="", flush=True)
