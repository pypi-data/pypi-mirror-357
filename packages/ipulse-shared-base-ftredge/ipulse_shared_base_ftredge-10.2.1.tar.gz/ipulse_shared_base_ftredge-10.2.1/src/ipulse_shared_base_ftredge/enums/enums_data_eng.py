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


class PipelineTrigger(AutoLower):
    MANUAL = auto()
    SCHEDULER =  auto()
    SCHEDULER_MAIN = auto()
    SCHEDULER_FALLBACK = auto()
    SCHEDULER_RETRY = auto()
    SCHEDULER_VERIFICATION = auto()
    EVENT_GCS_UPLOAD= auto()
    EVENT_PUBSUB= auto()
    ANOTHER_PIPELINE = auto()

class DataPrimaryCategory(AutoLower):
    HISTORIC = auto() # Historical data, usually accurate and complete
    LIVE=auto() # Real-time data, not always certain, can have error. Live and Historic can intersect, depending if
    ARCHIVE=auto() # Archived data,usually not used for refernce but for long term storage and compliance.
    REFERENCE = auto() # Reference data, used for reference and mapping, for example dimensional tables
    ANALYTICS=auto() # Analytical data and modelling, derived from historical and prediction data. Normally shall be making Human readable sense. vs. Features
    FEATURES=auto() # Feature data, used for training models
    PREDICTIONS=auto() # Predictive data, based on models and simulations
    SIMULATION=auto() # Simulation data, based on models and simulations
    SHARED=auto() # Shared data, used for sharing data between systems
    MULTIPLE = auto() # Multiple categories, used for data that can belong to multiple categories


class DataSecondaryCategory(AutoLower): # Data about the Data
    DATA= auto()
    CATALOGS=auto()
    MONITORING=auto()
    METADATA= auto()
    CHANGELOG = auto()
    PIPELOGS= auto()
    GENERALLOGS= auto()
    TAGS = auto()
    COMMENTS = auto()


class Lineage(AutoLower):
    SOURCE_OF_TRUTH = auto()
    COPY= auto()
    DERIVED_DATA = auto()
    BACKUP = auto()
    TEMPORARY = auto()
    UNKNOWN = auto()

class DatasetScope(AutoLower):
    FULL_DATASET = auto()
    LATEST_RECORD = auto()
    INCREMENTAL_DATASET = auto()
    BACKFILLING_DATASET = auto()
    PARTIAL_DATASET = auto()
    FILTERED_DATASET = auto()
    METADATA = auto()
    SOURCING_METADATA = auto()
    DATASET_METADATA = auto()
    CHANGE_METADATA = auto()
    UNKNOWN = auto()



class Attribute(AutoLower):
    RECENT_DATE = auto()
    RECENT_TIMESTAMP = auto()
    RECENT_DATETIME = auto()
    OLDEST_DATE = auto()
    OLDEST_TIMESTAMP = auto()
    OLDEST_DATETIME = auto()
    MAX_VALUE = auto()
    MIN_VALUE = auto()
    TOTAL_COUNT = auto()
    TOTAL_SUM = auto()
    MEAN = auto()
    MEDIAN = auto()
    MODE = auto()
    STANDARD_DEVIATION = auto()
    NB_FIELDS_PER_RECORDS = auto()

class MatchCondition(AutoLower):
    EXACT = auto()
    PREFIX = auto()
    SUFFIX = auto()
    CONTAINS = auto()
    REGEX = auto()
    IN_RANGE = auto()
    NOT_IN_RANGE = auto()
    GREATER_THAN = auto()
    LESS_THAN = auto()
    GREATER_THAN_OR_EQUAL = auto()
    LESS_THAN_OR_EQUAL = auto()
    IN_LIST = auto()
    NOT_IN_LIST = auto()
    ON_FIELD_MATCH = auto()
    ON_FIELD_EQUAL = auto()
    ON_FIELDS_EQUAL_TO = auto()
    ON_FIELDS_COMBINATION = auto()
    NOT_APPLICABLE = auto()


class DuplicationHandling(AutoLower):
    RAISE_ERROR = auto()
    OVERWRITE = auto()
    INCREMENT = auto()
    SKIP = auto()
    SYSTEM_DEFAULT = auto()
    ALLOW = auto() ## applicable for databases allowing this operation i.e. BigQuery
    MERGE_DEFAULT = auto()
    MERGE_PRESERVE_SOURCE_ON_DUPLICATES = auto()
    MERGE_PRESERVE_TARGET_ON_DUPLICATES = auto()
    MERGE_PRESERVE_BOTH_ON_DUPLICATES = auto()
    MERGE_RAISE_ERROR_ON_DUPLICATES = auto()
    MERGE_CUSTOM = auto()


class DuplicationHandlingStatus(AutoLower):
    ALLOWED = auto()
    RAISED_ERROR = auto()
    SYSTEM_DEFAULT = auto()
    OVERWRITTEN = auto()
    SKIPPED = auto()
    INCREMENTED = auto()
    OPERATION_CANCELLED = auto()
    MERGED = auto()
    MERGED_PRESERVED_SOURCE = auto()
    MERGED_PRESERVED_TARGET = auto()
    MERGED_PRESERVED_BOTH = auto()
    MERGED_RAISED_ERROR = auto()
    MERGED_CUSTOM = auto()
    NO_DUPLICATES = auto()
    UNKNOWN = auto()
    UNEXPECTED_ERROR= auto()
    CONDITIONAL_ERROR = auto()
    NOT_APPLICABLE = auto()


class CodingLanguage(AutoLower):
    PYTHON = auto()
    NODEJS = auto()
    JAVA = auto()
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    REACTJS = auto()


class CloudProvider(AutoLower):
    GCP = auto()
    AWS = auto()
    AZURE = auto()
    IBM = auto()
    ALIBABA = auto()
    NO_CLOUD = auto()
    CLOUD_AGNOSTIC = auto()
    OTHER = auto()
    UNKNOWN = auto()
class FileExtension(StrEnum):

    JSON = ".json"
    CSV = ".csv"
    EXCEL = ".xlsx"
    TXT = ".txt"
    PDF = ".pdf"
    PARQUET = ".parquet"
    AVRO = ".avro"
    WORD = ".docx"
    PPT = ".pptx"
    HTML = ".html"
    MARKDOWN = ".md"
    XML = ".xml"
    YAML = ".yaml"
    TOML = ".toml"
    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"