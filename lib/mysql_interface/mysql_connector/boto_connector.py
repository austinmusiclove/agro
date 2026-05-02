import os
import boto3
from typing import Any
from .interface import MySQLConnectorInterface


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


def _to_rds_params(params: list) -> list:
    if not params:
        return []
    return [
        {"name": f"p{i}", "value": {_infer_param_type(v): v}}
        for i, v in enumerate(params)
    ]


def _records_to_dicts(records: list, column_metadata: list) -> list[dict]:
    if not records:
        return []
    columns = [col.get("name") for col in column_metadata] if column_metadata else []
    result = []
    for row in records:
        row_dict = {}
        for i, field in enumerate(row):
            col_name = columns[i] if i < len(columns) else f"col_{i}"
            val = list(field.values())[0] if isinstance(field, dict) else field
            row_dict[col_name] = val
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

    def _execute(self, sql: str, params: list = None) -> dict:
        kwargs = {
            "resourceArn": self.resource_arn,
            "secretArn": self.secret_arn,
            "database": self.database,
            "sql": sql,
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
