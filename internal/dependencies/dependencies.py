import boto3
from botocore.config import Config


_config = Config(max_pool_connections=50)

db_connection = boto3.client("dynamodb", region_name="ap-south-1", config=_config)
