from enum import IntEnum, IntFlag, auto, nonmember

class Format(IntFlag):
    NONE = auto()
    BOLD = auto()
    DARKENED = auto()
    ITALIC = auto()
    UNDERLINE = auto()
    INVERSED = auto()
    INVISIBLE = auto()
    STRIKETHROUGH = auto()

    CODES = nonmember({
        NONE: 0,
        BOLD: 1,
        DARKENED: 2,
        ITALIC: 3,
        UNDERLINE: 4,
        INVERSED: 7,
        INVISIBLE: 8,
        STRIKETHROUGH: 9
    })

    def _to_list(self) -> list[str]:
        result = list()
        for style in self:
            result.append(str(self.CODES[style]))
        return result

class TextColor(IntEnum):
    GRAY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PINK = 35
    CYAN = 36
    WHITE = 37

class BackgroundColor(IntEnum):
    DARK_BLUE = 40
    ORANGE = 41
    MARBLE_BLUE = 42
    DARK_GRAY = 43
    GRAY = 44
    INDIGO = 45
    LIGHT_GRAY = 46
    WHITE = 47

def ansi_code(text_color: TextColor = None, bg_color: BackgroundColor = None, format: Format = None) -> str:
    code_list = ([str(text_color)] if text_color else []) \
                + ([str(bg_color)] if bg_color else []) \
                + (format._to_list() if format else [])
    if len(code_list) == 0:
        code_list = ['0']
    return "\u001b[" + ";".join(code_list) + "m"
