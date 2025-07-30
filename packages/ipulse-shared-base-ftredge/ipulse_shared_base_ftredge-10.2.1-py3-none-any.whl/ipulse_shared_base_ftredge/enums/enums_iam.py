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



class IAMUnitType(AutoLower):
    GROUPS = auto()
    ROLES = auto()
    PERMISSIONS = auto()


class IAMAction(AutoLower):
    ALLOW = auto()
    DENY = auto()
    GRANT = auto()
    REVOKE = auto()


class IAMUserType(AutoLower):
    ANONYMOUS = auto()
    AUTHENTICATED = auto()
    CUSTOMER = auto()
    EXTERNAL = auto()
    PARTNER = auto()
    INTERNAL = auto()
    EMPLOYEE = auto()
    SYSTEM = auto()
    ADMIN = auto()
    SUPERADMIN = auto()
