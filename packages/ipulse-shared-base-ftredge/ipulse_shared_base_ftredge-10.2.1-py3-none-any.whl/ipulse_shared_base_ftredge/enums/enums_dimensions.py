# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import StrEnum, unique
# ──────────────────────────────────────────────────────────────────────────────
# Abstract marker – lets you type-hint a generic “kind of enum we serialise”.
# ──────────────────────────────────────────────────────────────────────────────
class Dimension(StrEnum):
    """Marker base for all serialisable dimension / code enums."""

# ──────────────────────────────────────────────────────────────────────────────
# Financial or *countable* units
# ──────────────────────────────────────────────────────────────────────────────
@unique
class FinancialUnit(Dimension):
    """Units commonly used in finance and data-commerce."""
    SHARE = "share"               # Number of shares
    BPS = "bps"                   # Basis points
    PERCENT = "percent"           # %
    INDEX_POINT = "index_point"
    RATIO = "ratio"
    COUNT = "count"
    ITEM = "item"
    RECORD = "record"             # Generic record
    ROW = "row"
    COLUMN = "column"
    UNIT = "unit"                 # Fallback generic


# ──────────────────────────────────────────────────────────────────────────────
# Mass / Volume / Length units
# ──────────────────────────────────────────────────────────────────────────────
@unique
class MassUnit(Dimension):
    GRAM = "g"
    KILOGRAM = "kg"
    TONNE = "t"
    POUND = "lb"
    OUNCE = "oz"
    TROY_OUNCE = "ozt"

@unique
class VolumeUnit(Dimension):
    LITRE = "l"
    BARREL = "bbl"
    GALLON = "gal"

@unique
class AreaUnit(Dimension):
    SQUARE_METER = "m2"
    SQUARE_FOOT = "ft2"
    ACRE = "acre"


# ──────────────────────────────────────────────────────────────────────────────
# Memory & time units
# ──────────────────────────────────────────────────────────────────────────────
@unique
class MemoryUnit(Dimension):
    BYTE = "BYTE"
    KILOBYTE = "KILOBYTE"
    MEGABYTE = "MEGABYTE"
    GIGABYTE = "GIGABYTE"
    TERABYTE = "TERABYTE"
    PETABYTE = "PETABYTE"
    EXABYTE = "EXABYTE"



@unique
class DataUnit(Dimension):
    ROW = "row"                # Generic row
    FIELD = "field"            # Generic field
    RECORD = "record"          # Generic record
    DOCUMENT = "document"      # Generic document
    TABLE = "table"            # Generic table
    COLLECTION = "collection"  # Generic collection
    MESSAGE = "message"          # Generic message
    FILE = "file"              # Generic file
    DATABASE = "database"        # Generic database



@unique
class TimeUnit(Dimension):
    NANOSECOND = "nanosecond"
    MICROSECOND = "microsecond"
    MILLISECOND = "millisecond"
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


# ──────────────────────────────────────────────────────────────────────────────
# Market bar sizes / time frames
# ──────────────────────────────────────────────────────────────────────────────
@unique
class TimeFrame(Dimension):
    """Common bar sizes for market data (a.k.a. candle durations)."""
    ONE_MIN = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    ONE_H = "1h"
    TWO_H = "2h"
    FOUR_H = "4h"
    SIX_H = "6h"
    TWELVE_H = "12h"
    ONE_D = "1d"
    TWO_D = "2d"
    THREE_D = "3d"
    ONE_W = "1w"
    ONE_M = "1m"
    TWO_M = "2m"
    THREE_M = "3m"
    SIX_M = "6m"
    ONE_Y = "1y"
    THREE_Y = "3y"
    EOD = "eod"


# ──────────────────────────────────────────────────────────────────────────────
# Days of week / schedule codes
# ──────────────────────────────────────────────────────────────────────────────
@unique
class DayOfWeek(Dimension):
    """ISO-8601 weekday numbers with helpful bundles."""
    MONDAY = "1"
    TUESDAY = "2"
    WEDNESDAY = "3"
    THURSDAY = "4"
    FRIDAY = "5"
    SATURDAY = "6"
    SUNDAY = "7"

    # Combined codes (keep as strings to avoid numeric ambiguity)
    MON_THU = "1-4"
    MON_FRI = "1-5"
    MON_SAT = "1-6"
    WEEKEND = "6-7"
    SUN_THU = "7-4"
    ALL_DAYS = "1-7"

# ──────────────────────────────────────────────────────────────────────────────
# Currency ISO-4217 codes
# ──────────────────────────────────────────────────────────────────────────────
@unique
class Currency(Dimension):
    AED = "AED"
    AUD = "AUD"
    BRL = "BRL"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    EUR = "EUR"
    GBP = "GBP"
    HKD = "HKD"
    INR = "INR"
    JPY = "JPY"
    KRW = "KRW"
    MXN = "MXN"
    NOK = "NOK"
    NZD = "NZD"
    RUB = "RUB"
    SEK = "SEK"
    SGD = "SGD"
    USD = "USD"
    ZAR = "ZAR"


