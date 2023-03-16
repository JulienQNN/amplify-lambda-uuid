import json
import os

import boto3

secretmanager = boto3.client("secretsmanager")
lambdaEvent = boto3.client("lambda")


def handler(event, context):
    if event:
        body = json.loads(event["body"])
        print(body)
        token = event["headers"]["x-api-key"]
        print(token)
        data = body["data"]
        action = body["action"]

        if token:
            user_id = get_user_id_in_secret("userSecret", token)
            payload = {"data": data, "userId": user_id}

            if not user_id:
                return api_response(
                    status_code=405, body=json.dumps("NO USER EXIST WITH THIS TOKEN")
                )

            if action == "DB":
                lambdaEvent.invoke(
                    FunctionName=os.environ["FUNCTION_AMPLIFYADDUSER_NAME"],
                    Payload=json.dumps(payload),
                )
                return api_response(
                    status_code=200, body=json.dumps("DATA INSERTED IN DYNAMODB")
                )
            if action == "S3":
                response = lambdaEvent.invoke(
                    FunctionName=os.environ["FUNCTION_ADDDATAS3_NAME"],
                    Payload=json.dumps(payload),
                )

                return api_response(
                    status_code=200,
                    body=json.dumps(response["Payload"].read().decode()),
                )

    return api_response(status_code=405, body=json.dumps("TOKEN MISSING"))


def get_user_id_in_secret(secret_name, secret_key):
    secret_object = secretmanager.get_secret_value(SecretId=secret_name)
    secret_values = json.loads(secret_object["SecretString"])

    for key in secret_values:
        if key == secret_key:
            return secret_values[key]


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
