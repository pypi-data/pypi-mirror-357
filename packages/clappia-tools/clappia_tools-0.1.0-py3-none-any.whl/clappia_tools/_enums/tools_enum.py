from enum import Enum


class FilterOperator(Enum):
    CONTAINS = "CONTAINS"
    NOT_IN = "NOT_IN"
    EQ = "EQ"
    NEQ = "NEQ"
    EMPTY = "EMPTY"
    NON_EMPTY = "NON_EMPTY"
    STARTS_WITH = "STARTS_WITH"
    BETWEEN = "BETWEEN"
    GT = "GT"
    LT = "LT"
    GTE = "GTE"
    LTE = "LTE"


class LogicalOperator(Enum):
    AND = "AND"
    OR = "OR"


class FilterKeyType(Enum):
    STANDARD = "STANDARD"
    CUSTOM = "CUSTOM"


class AggregationType(Enum):
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    UNIQUE = "unique"


class DimensionType(Enum):
    STANDARD = "STANDARD"
    CUSTOM = "CUSTOM"


class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class DataType(Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SELECT = "select"
    TEXT_INPUT = "textInput"


class LanguageCode(Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"


class FieldType(Enum):
    SINGLE_LINE_TEXT = "singleLineText"
    MULTI_LINE_TEXT = "multiLineText"
    RICH_TEXT_EDITOR = "miniRichTextEditor"
    NUMBER_INPUT = "numberInput"
    SINGLE_SELECTOR = "singleSelector"
    MULTI_SELECTOR = "multiSelector"
    DATE_TIME = "dateTime"
    FILE_UPLOAD = "fileUpload"
    LOCATION = "location"
    SIGNATURE = "signature"
    CAMERA = "camera"
    BARCODE_SCANNER = "barcodeScanner"
    NFC_READER = "nfcReader"
    BUTTON = "button"
    CALCULATIONS = "calculations"
    NESTED_FORM = "nestedForm"
