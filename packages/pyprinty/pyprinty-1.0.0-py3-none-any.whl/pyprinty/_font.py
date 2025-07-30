from _colors import Colors
from _effects import Effects
import _show


class Ready:
    FONT_ERROR = {
        "base_color": Colors.RED,
        "text_color": Colors.WHITE,
        "effects": [Effects.Bold, Effects.Speedblink]
    }
    FONT_ERROR2 = {
        "base_color": Colors.BLACK,
        "text_color": Colors.RED,
        "effects": [Effects.Bold, Effects.Dubleline]
    }
    FONT_TITLE = {
        "base_color": Colors.BLACK,
        "text_color": Colors.YELLOW,
        "effects": [Effects.Bold, Effects.Upline, Effects.Italic]
    }
    FONT_HANDWRITING = {
        "base_color": Colors.BLACK,
        "text_color": Colors.GRAY,
        "effects": [Effects.Italic, Effects.Dim]
    }
    FONT_LOW = {
        "base_color": Colors.BLACK,
        "text_color": Colors.MAGENTA,
        "effects": [Effects.Dim]
    }
    FONT_HIGH = {
        "base_color": Colors.BLACK,
        "text_color": Colors.GREEN,
        "effects": [Effects.Bold]
    }
    FONT_CLASSIC = {
        "base_color": Colors.BLACK,
        "text_color": Colors.CYAN,
        "effects": []
    }
    FONT_CANCELED = {
        "base_color": Colors.BLACK,
        "text_color": Colors.BLUE,
        "effects": [Effects.Strikethrough]
    }
    FONT_MESSAGE = {
        "base_color": Colors.WHITE,
        "text_color": Colors.BLUE,
        "effects": []
    }
    FONT_IMPORTANT_MESSAGE = {
        "base_color": Colors.WHITE,
        "text_color": Colors.ORANGE,
        "effects": [Effects.Blink]
    }
    FONT_IMPORTANT_MESSAGE2 = {
        "base_color": Colors.RED,
        "text_color": Colors.GREEN,
        "effects": [Effects.Underline]
    }


class Font:
    def __init__(
            self, base_color=None, text_color=None, shine_color=None,
            text=True, shine_width=2, effects=None,steps=255, time=1,
            location_start=None, location_end=None ,load=None
    ):
        self.base_color = base_color or Colors.BLACK
        self.text_color = text_color or Colors.WHITE
        self.shine_color = shine_color or Colors.BLACK
        self.location_start = location_start or []
        self.location_end = location_end or []
        self.effects = effects or []
        self.text = text
        self.shine_width = shine_width
        self.steps = steps
        self.time = time

        if load:
            for i in load.items():
                setattr(self, i[0], i[1])

    def __call__(self, *text, location=True, sep=" ",file=None):
        print("\033[0m", end="\r", flush=True)
        return ("".join(self.location_start) if location else "") +\
            self.text_color.string() + self.base_color.string(text=False) +\
            "".join(self.effects) + sep.join(text) + ("".join(self.location_end) if location else "")

    def sun(self, *text, file=None, sep=" ", end="\n"):
        _show.sun(self, *text, file=file, sep=sep, end=end)


    def rank(self, *text, file=None, sep=" ", end="\n"):
        _show.rank(self, *text, file=file, sep=sep, end=end)
