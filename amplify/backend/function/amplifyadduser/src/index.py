import json

import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")


def handler(event, context):
    table = dynamodb.Table("userId-dev")

    if event:
        insert_user(table, event)
        return api_response(status_code=200, body=json.dumps("INSERT DONE"))

    return api_response(status_code=401, body=json.dumps("COULD NOT INSERT"))


def insert_user(table, payload):
    return table.put_item(Item={"id": payload["userId"], "data": payload["data"]})


def api_response(body, status_code):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": body,
    }
