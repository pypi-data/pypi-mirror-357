from typing import Generator


def levels_generator(start_color: tuple[int, int, int], finish_color: tuple[int, int, int], levels: int) -> Generator:
    """
    This generator calculates the next color to print in a fixed progression,
    according to the given number of steps,
    so that it consistently reaches from the initial color to the final color.
    :param levels:
    :param start_color:
    :param finish_color:
    :return:
    """
    get_color = lambda a, b, c, d: int(a + (float(c) / (d - 1)) * (b - a))  # Formula for calculating color intensity
    for step in range(levels):
        # Finds the final RGB color for each step
        yield tuple(get_color(start_color[x], finish_color[x], step, levels) for x in range(3))
