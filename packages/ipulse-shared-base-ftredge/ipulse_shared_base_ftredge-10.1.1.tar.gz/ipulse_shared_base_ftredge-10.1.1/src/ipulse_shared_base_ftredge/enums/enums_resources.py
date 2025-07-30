
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


class Resource(AutoLower):
    pass


class DataResource(Resource):

    UNKNOWN= auto()
    NOTSET= auto()

    # --- Generic Reference ---
    DATA = auto()
    IN_MEMORY_DATA = auto()
    METADATA= auto()
    IN_MEMORY_METADATA = auto()
    CONFIG = auto()
    # --- COMMUNICATION  ---
    API = auto()
    API_INTERNAL = auto()
    API_EXTERNAL = auto()
    WEBSITE = auto()
    INTERNET = auto()
    RPC = auto()
    GRPC = auto()

    # --- Messaging ---
    MESSAGING_KAFKA = auto()
    MESSAGING_SQS = auto()
    MESSAGING_PUBSUB_TOPIC = auto()
    # --- Real-time Communication ---
    REALTIME_WEBSOCKET = auto()
     # --- Notifications ---
    NOTIFICATION_WEBHOOK = auto()

    #-----------------
    #------ DBs ------
    #-----------------

    # --Generic Reference --
    DB= auto()
    DB_TABLE = auto()
    DB_RECORD = auto()
    DB_COLLECTION = auto()
    DB_DOCUMENT = auto()
    DB_VIEW = auto()

    # --SQL Databases--
    DB_ORACLE = auto()
    DB_POSTGRESQL = auto()
    DB_SQLSERVER = auto()
    DB_MYSQL = auto()
    DB_BIGQUERY = auto()
    DB_BIGQUERY_TABLE = auto()
    DB_SNOWFLAKE = auto()
    DB_REDSHIFT = auto()
    DB_ATHENA = auto()
    # --NOSQL Databases--
    DB_MONGO = auto()
    DB_REDIS = auto()
    DB_CASSANDRA = auto()
    DB_NEO4J = auto()
    DB_FIRESTORE = auto()
    DB_FIRESTORE_DOC = auto()
    DB_FIRESTORE_COLLECTION = auto()
    DB_DYNAMODB = auto()
    # --NEWSQL Databases--
    DB_COCKROACHDB = auto()
    DB_SPANNER = auto()

    # --- Storage and DATA ---
    GCP_SECRET_MANAGER = auto()
    LOCAL_STORAGE = auto()
    GCS = auto()
    S3 = auto()
    AZURE_BLOB = auto()
    HDFS = auto()
    NFS = auto()
    FTP = auto()
    SFTP = auto()
    # --- Files ---
    FILE = auto()
    FILE_JSON = auto()
    FILE_CSV = auto()
    FILE_EXCEL = auto()
    FILE_TXT = auto()
    FILE_PDF = auto()
    FILE_PARQUET = auto()
    FILE_AVRO = auto()
    FILE_WORD = auto()
    FILE_PPT = auto()
    FILE_HTML = auto()
    FILE_MARKDOWN = auto()
    FILE_XML = auto()
    FILE_YAML = auto()
    FILE_TOML = auto()
    FILE_JPG = auto()
    FILE_JPEG = auto()
    FILE_PNG = auto()

class ComputeResource(Resource):

    # --- Compute ---
    CLOUD_FUNCTION = auto()
    CLOUD_RUN= auto()
    CLOUD_RUN_SERVICE = auto()
    CLOUD_RUN_JOB = auto()
    CLOUD_COMPUTE_ENGINE = auto()
    CLOUD_DATAPROC = auto()
    CLOUD_DATAFLOW = auto()
    CLOUD_BIGQUERY = auto()
    CLOUD_LAMBDA = auto()
    CLOUD_EC2 = auto()
    CLOUD_EMR = auto()
    CLOUD_GLUE = auto()
    CLOUD_ATHENA = auto()
    CLOUD_REDSHIFT = auto()
    CLOUD_SYNAPSE_ANALYTICS = auto()
    CLOUD_DATA_FACTORY = auto()
    CLOUD_VIRTUAL_MACHINES = auto()
    CLOUD_COMPUTE = auto()
    CLOUD_DOCKER = auto()
    CLOUD_KUBERNETES = auto()
    CLOUD_GKE = auto()
    CLOUD_AKS = auto()
    CLOUD_EKS = auto()
    CLOUD_AZURE_FUNCTIONS = auto()
    CLOUD_AZURE_VIRTUAL_MACHINES = auto()
    CLOUD_AZURE_SYNAPSE_ANALYTICS = auto()
    CLOUD_AZURE_DATA_FACTORY = auto()
    CLOUD_AZURE_DATABRICKS = auto()
    CLOUD_AZURE_ANALYTICS = auto()
    CLOUD_AZURE_SQL = auto()
    CLOUD_AZURE_COSMOSDB = auto()
    CLOUD_AZURE_TABLE = auto()
    CLOUD_AZURE_BLOB = auto()
    CLOUD_AZURE_FILE = auto()
    CLOUD_AZURE_QUEUE = auto()
    CLOUD_AZURE_EVENTHUB = auto()
    CLOUD_AZURE_NOTIFICATIONHUB = auto()
    CLOUD_AZURE_CACHE = auto()
    CLOUD_AZURE_REDIS = auto()
    CLOUD_AZURE_SEARCH = auto()
    LOCAL_COMPUTE = auto()
    LOCAL_JUPYTER_NOTEBOOK = auto()
    LOCAL_SCRIPT = auto()
    LOCAL_SERVER = auto()
    LOCAL_DOCKER = auto()
    LOCAL_KUBERNETES = auto()
    LOCAL_GCP_CLOUD_FUNCTION = auto()


class ProcessorResource(Resource):

    CPU_INTEL = auto()
    CPU_AMD = auto()
    CPU_ARM = auto()
    GPU_NVIDIA = auto()
    GPU_AMD = auto()
    GPU_INTEL = auto()
    TPU_GOOGLE = auto()
    TPU_INTEL = auto()
    TPU_AMD = auto()

class AbstractResource(Resource):
    MICROSERVICE = auto()
    MICROSERVMON = auto()
    MICROSERVICE_TRACE = auto()

    PIPELINE= auto()
    PIPELINEFLOW= auto()
    PIPELINEMON= auto()
    PIPELINE_STEP= auto()
    PIPELINE_TASK = auto()
    PIPELINE_OPERATION = auto()
    PIPELINE_TASK_SEQUENCE = auto()
    PIPELINE_GROUP= auto()
    PIPELINE_DYNAMIC_ITERATOR = auto()
    PIPELINE_ITERATION = auto()
    PIPELINE_SUBJECT= auto()
    PIPELINE_SUBJECT_SEQUENCE= auto()

    RECORD= auto()
    SCRIPT = auto()
    JOB= auto()
