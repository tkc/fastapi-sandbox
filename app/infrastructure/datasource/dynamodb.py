from typing import Any

import boto3

from app.core.config import settings


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
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "name", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "name-index",
                "KeySchema": [
                    {"AttributeName": "name", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            },
            {
                "IndexName": "email-index",
                "KeySchema": [
                    {"AttributeName": "email", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            },
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )
    table.wait_until_exists()
    return table
