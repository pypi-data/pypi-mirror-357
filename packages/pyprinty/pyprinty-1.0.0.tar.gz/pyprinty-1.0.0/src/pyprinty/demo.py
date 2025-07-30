import time
from _animation import Animation
from _effects import Cursor, Effects
from _colors import Color
from _font import Font
from _terminal import good


def demo2():
    if not good():
        print("is not good terminal!")
        while True:
            pass
    c = """██████╗ ██╗   ██╗██████╗ ██████╗ ██╗███╗   ██╗████████╗██╗   ██╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝╚██╗ ██╔╝
██████╔╝ ╚████╔╝ ██████╔╝██████╔╝██║██╔██╗ ██║   ██║    ╚████╔╝ 
██╔═══╝   ╚██╔╝  ██╔═══╝ ██╔═══╝ ██║██║╚██╗██║   ██║     ╚██╔╝  
██║        ██║   ██║     ██║     ██║██║ ╚████║   ██║      ██║   
╚═╝        ╚═╝   ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═══╝   ╚═╝      ╚═╝   """
    sss = [63, 128, 127, 192, 191, 256, 255, 320, 385, 384, 383, 252, 186, 123,120, 57, 54, 119,
           118, 117, 116, 181, 246, 311, 376, 375, 374, 113, 112, 111, 45, 110, 175, 240, 305,
           370, 369, 368, 367, 366, 300, 237, 234, 171, 105, 39, 168, 233, 298, 363, 362, 361,
           35, 100, 165, 230, 295, 360, 359, 358, 31, 97, 162, 161, 226, 225, 224, 223, 222, 287,
           352, 351, 350, 94, 93, 92, 23, 89, 154, 153, 218, 217, 216, 215, 214, 279, 344, 343,
           342, 86, 85, 84, 16, 81, 80, 145, 144, 209, 208, 273, 338, 337, 336, 205, 139, 76, 73,
           10, 6, 72, 137, 136, 201, 200, 199, 198, 197, 262, 327, 326, 325, 67, 68, 69
           ]


    def render_text(state):
        output = ""
        last_color = None
        for ch, col in state:
            if col != last_color:
                output += col.string()
                last_color = col
            output += ch
        output += Effects.CLEAR_EFFECTS
        return output

    text_state = [(ch, Color(255, 255, 255)) for ch in c]
    Cursor.PRINT(Cursor.HIDE)
    my_an = Animation(load={"c": {"font": Font(), "mode": "print"},
                            "b": {"font": Font(), "mode": "print"}})

    for i in sss:
        text_state[i] = (text_state[i][0], Color(255, 0, 0))
        Cursor.PRINT(Cursor.CLEAR_ALL)
        my_an.send("c", render_text(text_state))
        time.sleep(0.03)
    for v in range(255):
        time.sleep(0.005)
        Cursor.PRINT(Cursor.CLEAR_ALL)
        for i in c:
            if i == "█":
                print(Color(0, 255 - v, 0).string() + i, end="")
            elif i in [" ", "\n"]:
                print(i, end="")
            else:
                print(Color(255 - v, 0, 0).string() + i, end="")
    text_state = [(ch, Color(0, 0, 0)) for ch in c]
    for i in sss:
        text_state[i] = (text_state[i][0], Color(0, 0, 255))
        Cursor.PRINT(Cursor.CLEAR_ALL)
        my_an.send("c", render_text(text_state))
        time.sleep(0.01)
    for v in range(255):
        time.sleep(0.001)
        Cursor.PRINT(Cursor.CLEAR_ALL)
        for i in c:
            if i == "█":
                print(Color(0, v, 0).string() + i, end="")
            elif i in [" ", "\n"]:
                print(i, end="")
            else:
                print(Color(255, 0, 0).string() + i, end="")
    time.sleep(0.5)

demo2()
