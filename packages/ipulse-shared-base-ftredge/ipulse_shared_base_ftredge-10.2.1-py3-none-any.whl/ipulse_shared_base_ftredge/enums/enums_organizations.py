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


class OrganizationRelation(AutoLower):
    """Organization relationship types"""

    RETAIL_CUSTOMER = auto()
    CORPORATE_CUSTOMER = auto()
    PARENT = auto()
    SISTER = auto()
    SELF = auto()
    PARTNER = auto()
    SUPPLIER = auto()
    SPONSOR = auto()
    INVESTOR = auto()
    REGULATOR = auto()
    OTHER = auto()

class OrganizationIndustry(AutoLower):
    """Organization industry types"""
    DATA = auto()
    GOVERNMENT = auto()
    MEDIA = auto()
    ACADEMIC = auto()
    COMMERCIAL = auto()
    FUND = auto()
    FINANCE = auto()
    ADVISORY = auto()
    HEDGEFUND = auto()
    BANK = auto()
    VC = auto()
    PE = auto()
    CONSTRUCTION = auto()
    HEALTHCARE = auto()
    TECHNOLOGY = auto()
    CONSULTING = auto()
    RETAIL = auto()
    NON_PROFIT = auto()
    INDIVIDUAL = auto()
    FREELANCER = auto()
    OTHER = auto()