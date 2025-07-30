# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import StrEnum, auto

class AutoLower(StrEnum):
    """
    StrEnum contrary to simple Enum is of type `str`, so it can be used as a string.
    StrEnum whose `auto()` values are lower-case.
    (Identical to StrEnum's own default, but keeps naming symmetrical.)
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()            # StrEnum already does this

class AutoUpper(StrEnum):
    """
    StrEnum contrary to simple Enum is of type `str`, so it can be used as a string.
    StrEnum whose `auto()` values stay as-is (UPPER_CASE).
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name                    # keep original upper-case


# ────────────────────────────────────────────────────────
# 0. Data-domain category (what the record IS)
# ────────────────────────────────────────────────────────
class FinCoreCategory(AutoLower):
    MARKET           = auto()   # prices, trades, quotes
    FUNDAMENTAL      = auto()   # financial statements
    CORPORATE_EVENTS = auto()   # dividends, splits, M&A
    ECONOMIC         = auto()   # macro time-series
    ALTERNATIVE      = auto()   # news, tweets, satellite…
    DERIVED          = auto()   # indicators, sentiment
    REFERENCE        = auto()   # static ids, calendars
    OTHER            = auto()


# ────────────────────────────────────────────────────────
# 1. Top-level economic exposure (stock / bond …)
# ────────────────────────────────────────────────────────
class MarketAssetCategory(AutoLower):
    STOCK        = auto()
    BOND         = auto()
    COMMODITY    = auto()
    FX           = auto()
    CRYPTO       = auto()
    REAL_ESTATE  = auto()
    FUND         = auto()
    OTHER        = auto()


# ────────────────────────────────────────────────────────
# 2. Finer sub-families
# ────────────────────────────────────────────────────────
class MarketAssetSubCategory(AutoLower):
    # — Stocks —
    COMMON_STOCK            = auto()
    PREFERRED_STOCK         = auto()
    DEPOSITARY_RECEIPT_ADR  = auto()
    DEPOSITARY_RECEIPT_GDR  = auto()
    REIT                    = auto()
    SPAC                    = auto()

    # — Bonds —
    GOVERNMENT_BOND         = auto()
    CORPORATE_BOND          = auto()
    MUNICIPAL_BOND          = auto()
    CONVERTIBLE_BOND        = auto()
    PERPETUAL_NOTE          = auto()
    SUKUK                   = auto()

    # — Commodities —
    METAL                   = auto()
    ENERGY                  = auto()
    AGRICULTURE             = auto()

    # — FX —
    MAJOR_CURRENCY          = auto()
    EM_CURRENCY             = auto()

    # — Crypto —
    COIN                    = auto()
    TOKEN                   = auto()
    STABLECOIN              = auto()
    DEFI_GOV                = auto()

    # — Funds & Real-estate —
    MUTUAL_FUND             = auto()
    INDEX_FUND              = auto()
    PRIVATE_RE              = auto()
    LISTED_RE               = auto()

    OTHER                   = auto()


# ────────────────────────────────────────────────────────
# 3. Contract / wrapper form (spot, future, ETF …)
# ────────────────────────────────────────────────────────
class MarketInstrumentType(AutoLower):
    SPOT     = auto()
    FUTURE   = auto()
    OPTION   = auto()
    SWAP     = auto()
    FORWARD  = auto()
    ETF      = auto()
    CFD      = auto()
    INDEX    = auto()
    ADR      = auto()
    OTHER    = auto()


# ────────────────────────────────────────────────────────
# 4. Granular market-data record type
# ────────────────────────────────────────────────────────
class MarketRecordType(AutoLower):
    TRADE          = auto()
    SPOT           = auto()
    OPEN           = auto()
    HIGH           = auto()
    LOW            = auto()
    CLOSE          = auto()
    VOLUME         = auto()
    ADJC           = auto()
    ADJC_CLOSE     = auto()
    ADJC_VOLUME    = auto()
    HIGH_LOW       = auto()
    CLOSE_VOLUME   = auto()
    HLV            = auto()
    OHLC           = auto()
    OHLCV          = auto()
    OHLCVA         = auto()
    OTHER          = auto()

class MarketExchange(AutoUpper):
    CC = auto()
    US = auto()
    NASDAQ = auto()
    NYSE = auto()
    SHG = auto()
    LSE = auto()