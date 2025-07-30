
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
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



class Layer(StrEnum):
    PULSE_APP="papp"
    PULSE_MSG="pmsg"
    DATA_PLATFORM="dp"
    
class Module(AutoLower):
    SHARED=auto()
    CORE=auto()
    ORACLE=auto()
    PORTFOLIO=auto()
    RISK=auto()
    RESEARCH=auto()
    TRADING=auto()
    SIMULATION=auto()


class Subject(AutoLower):
    USER=auto()
    ORGANIZATION=auto()
    DEPARTMENT = auto()
    WORKSPACE = auto()
    GROUP=auto()
    SUBSCRIPTION=auto()
    CATALOG=auto()
    PAYMENT=auto()
    ACTION=auto()
    DATASET=auto()
    RESOURCE=auto()
    SERVICE=auto()
    ROLE=auto()


class SubscriptionPlan(AutoLower):
    NO_SUBSCRIPTION=auto()
    FREE_SUBSCRIPTION=auto()
    BASE_SUBSCRIPTION=auto()
    PREMIUM_SUBSCRIPTION=auto()
    ADVANCED_SUBSCRIPTION=auto()
    PROFESSIONAL_SUBSCRIPTION=auto()
    ENTERPRISE_SUBSCRIPTION=auto()


class Sector(AutoLower):
    FINCORE=auto()
    HEALTHCORE=auto()
    ENVICORE=auto()
    SPORTSCORE=auto()
    POLITCORE=auto()
    NEWSCORE=auto()
    PORTFOLIO=auto()
    RISK=auto()
    RESEARCH=auto()
    TRADING=auto()
    CUSTOM=auto()

    


