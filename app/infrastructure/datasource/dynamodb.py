from typing import Any

import boto3

from app.core.config import settings
from app.infrastructure.constants import (
    ATTR_EMAIL,
    ATTR_NAME,
    ATTR_USER_ID,
    DEFAULT_READ_CAPACITY,
    DEFAULT_WRITE_CAPACITY,
    INDEX_EMAIL,
    INDEX_NAME,
)


def get_dynamodb_resource() -> Any:
    return boto3.resource(
        "dynamodb",
        endpoint_url=settings.dynamodb_endpoint,
        region_name=settings.dynamodb_region,
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )


def get_table() -> Any:
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.dynamodb_table_name)


def create_users_table() -> Any:
    dynamodb = get_dynamodb_resource()
    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]
    if settings.dynamodb_table_name in existing_tables:
        return dynamodb.Table(settings.dynamodb_table_name)

    table = dynamodb.create_table(
        TableName=settings.dynamodb_table_name,
        KeySchema=[
            {"AttributeName": ATTR_USER_ID, "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": ATTR_USER_ID, "AttributeType": "S"},
            {"AttributeName": ATTR_NAME, "AttributeType": "S"},
            {"AttributeName": ATTR_EMAIL, "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": INDEX_NAME,
                "KeySchema": [
                    {"AttributeName": ATTR_NAME, "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": DEFAULT_READ_CAPACITY,
                    "WriteCapacityUnits": DEFAULT_WRITE_CAPACITY,
                },
            },
            {
                "IndexName": INDEX_EMAIL,
                "KeySchema": [
                    {"AttributeName": ATTR_EMAIL, "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": DEFAULT_READ_CAPACITY,
                    "WriteCapacityUnits": DEFAULT_WRITE_CAPACITY,
                },
            },
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={
            "ReadCapacityUnits": DEFAULT_READ_CAPACITY,
            "WriteCapacityUnits": DEFAULT_WRITE_CAPACITY,
        },
    )
    table.wait_until_exists()
    return table
