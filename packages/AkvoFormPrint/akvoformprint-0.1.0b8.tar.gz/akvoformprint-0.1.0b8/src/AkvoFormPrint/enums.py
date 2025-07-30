from enum import Enum


class QuestionType(str, Enum):
    CASCADE = "cascade"
    GEO = "geo"
    INPUT = "input"
    NUMBER = "number"
    DATE = "date"
    OPTION = "option"
    MULTIPLE_OPTION = "multiple_option"
    IMAGE = "image"
    TEXT = "text"
    TABLE = "table"
    AUTOFIELD = "autofield"
    TREE = "tree"
    SIGNATURE = "signature"
    INSTRUCTION = "instruction"


class AnswerFieldConfig(str, Enum):
    TEXTBOX = "textbox"
    OPTION_SINGLE_LINE = "option_single_line"
    INSTRUCTION = "instruction"


class HintText(str, Enum):
    OPTION = "Mark only one oval"
    MULTIPLE_OPTION = "Tick all that apply"
    DATE = "Fill in the date using structure DD/MM/YYYY"
