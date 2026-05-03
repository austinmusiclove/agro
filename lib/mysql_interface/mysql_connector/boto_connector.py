import os
import re
import time
import logging
import boto3
from typing import Any, Callable
from functools import wraps
from botocore.exceptions import ClientError
from .interface import MySQLConnectorInterface

logger = logging.getLogger(__name__)


def retry_on_resuming(max_retries: int = 3, delay: int = 5):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    if e.response["Error"]["Code"] == "DatabaseResumingException":
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Database resuming, retrying in {delay}s (attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(delay)
                            continue
                    raise
            raise Exception(f"Failed after {max_retries} retries due to DatabaseResumingException")
        return wrapper
    return decorator


def _infer_param_type(value: Any) -> str:
    if isinstance(value, bool):
        return "booleanValue"
    if isinstance(value, int):
        return "longValue"
    if isinstance(value, float):
        return "doubleValue"
    if isinstance(value, bytes):
        return "blobValue"
    return "stringValue"


def _convert_sql_placeholders(sql: str) -> str:
    """Convert ? placeholders to :p0, :p1, etc. for RDS Data API named parameters."""
    counter = [0]
    def replacer(match):
        result = f":p{counter[0]}"
        counter[0] += 1
        return result
    return re.sub(r'\?', replacer, sql)


def _to_rds_params(params: list) -> list:
    if not params:
        return []
    rds_params = []
    for i, v in enumerate(params):
        if v is None:
            rds_params.append({
                "name": f"p{i}",
                "value": {"isNull": True}
            })
        else:
            rds_params.append({
                "name": f"p{i}",
                "value": {_infer_param_type(v): v}
            })
    return rds_params


def _records_to_dicts(records: list, column_metadata: list) -> list[dict]:
    if not records:
        return []
    columns = []
    if column_metadata:
        for col in column_metadata:
            if isinstance(col, dict):
                columns.append(col.get("name", f"col_{len(columns)}"))
            else:
                columns.append(f"col_{len(columns)}")
    result = []
    for row in records:
        row_dict = {}
        for i, field in enumerate(row):
            col_name = columns[i] if i < len(columns) else f"col_{i}"
            if isinstance(field, dict):
                if field.get("isNull"):
                    row_dict[col_name] = None
                else:
                    row_dict[col_name] = list(field.values())[0]
            else:
                row_dict[col_name] = field
        result.append(row_dict)
    return result


class BotoConnector(MySQLConnectorInterface):
    def __init__(self, config_loader):
        super().__init__(config_loader)
        self.region = self._config.get("region", "us-east-2")
        self.resource_arn = self._config.get("resource_arn", "")
        self.secret_arn = self._config.get("secret_arn", "")
        self.database = self._config.get("database", "agro")
        self.client = boto3.client("rds-data", region_name=self.region)

    @retry_on_resuming(max_retries=3, delay=5)
    def _execute(self, sql: str, params: list = None) -> dict:
        # Convert ? placeholders to named parameters for RDS Data API
        sql = _convert_sql_placeholders(sql)
        kwargs = {
            "resourceArn": self.resource_arn,
            "secretArn": self.secret_arn,
            "database": self.database,
            "sql": sql,
            "includeResultMetadata": True,
        }
        if params:
            kwargs["parameters"] = _to_rds_params(params)
        return self.client.execute_statement(**kwargs)

    def execute_query(self, sql: str, params: list = None) -> list[dict]:
        response = self._execute(sql, params)
        records = response.get("records", [])
        column_metadata = response.get("columnMetadata", [])
        return _records_to_dicts(records, column_metadata)

    def execute_insert(self, sql: str, params: list = None) -> int:
        response = self._execute(sql, params)
        generated = response.get("generatedFields", [])
        if generated:
            return list(generated[0].values())[0]
        return 0

    def execute_update(self, sql: str, params: list = None) -> int:
        response = self._execute(sql, params)
        return response.get("numberOfRecordsUpdated", 0)

    def close(self):
        pass
