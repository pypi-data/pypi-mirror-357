def rank(font, *text, file=None, sep=" ", end="\n"):
    from time import sleep as sl  # Pause function
    from _colorsgenerator import levels_generator as lg  # Gradual color generator
    from _colors import Color  # Color printing function
    from sys import __stdout__ as st

    print("\033[0m" + "".join(font.location_start), end="\r", flush=True)
    file = file or st
    steps = max(font.steps, 2)  # Minimum number of steps - 2
    delay = font.time / steps  # The amount of time that must be waited between exchanges to reach the total desired time
    txt = sep.join(text)  # Converts the list of text values into a single string by sep
    R = "\b" * len(txt)

    for color in lg(font.shine_color.tuple, (font.text_color.tuple if font.text else font.base_color.tuple), steps):
        print(font(Color(*color).string(text=font.text) + txt, location=False), flush=True, file=file, end=R)
        sl(delay)

    print("".join(font.location_end), file=file, flush=True, end=font(end, location=False))  # Prints the ending after the effect


def sun(font, *text, file=None, sep=" ", end="\n"):
    from time import sleep as sl  # Pause function
    from sys import __stdout__ as st  # Default output pipe
    from _colors import Color

    print("\033[0m" + "".join(font.location_start), end="\r", flush=True)
    file = file or st
    shine_width = max(font.shine_width, 0)
    text = sep.join(text)
    colors = ((font.text_color.tuple  if font.text else font.base_color.tuple), font.shine_color.tuple)
    R = "\b" * len(text)

    def build_shiny_frame(pos):
        interpolate = lambda start, end, factor: int(start + (end - start) * factor)
        compute_color = lambda: tuple(interpolate(b, s, factor) for b, s in zip(*colors))
        colorize_char = lambda: color.string(text=font.text) + char
        result = ""
        for i, char in enumerate(text):
            factor = max(0, 1 - abs(i - pos) / (shine_width + 1))
            color = Color(*compute_color())
            result += colorize_char()
        return result + "\033[0m"

    i = 0
    delay = font.time / len(range(-shine_width, len(text) + shine_width + 1))
    for pos in range(-shine_width, len(text) + shine_width + 1):
        i += 1
        print(font(build_shiny_frame(pos), location=False), end=R, flush=True, file=file)
        sl(delay)

    print("".join(font.location_end), end=font(end, location=False), file=file, flush=True)
