import json
import os

import boto3

secretmanager = boto3.client('secretsmanager')
lambdaEvent = boto3.client('lambda')


def handler(event, context):
    print('received event:')
    print(event)

    if event['body']:
        token = event['body']['token']
        if token:
            user_id = get_user_id_in_secret("userSecret", token)
            print(user_id)
            if not user_id:
                return {
                    'statusCode': 405,
                    'headers': {
                        'Access-Control-Allow-Headers': '*',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    'body': json.dumps('no user_id affiliated with the token')
                }
            data_from_body = event['body']['data']
            payload = {
                'data': data_from_body,
                'userId': user_id
            }
            if event['body']['action'] == 'DB':
                print('AVANT DE CALL LA LAMBDA')
                lambdaEvent.invoke(
                    FunctionName=os.environ['FUNCTION_AMPLIFYADDUSER_NAME'],
                    Payload=json.dumps(payload),
                )
                return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Done')
    }
    return {
        'statusCode': 405,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('TOKEN MISSING')
    }
    #   check if token exist in db
    # check body['action']
    # action == S3 -> lambda for S3
    # action ==
    # return error
# 	return error


def get_user_id_in_secret(secret_name, secret_key):
    secret_object = secretmanager.get_secret_value(SecretId=secret_name)
    secret_values = json.loads(secret_object["SecretString"])
    
    for key in secret_values:
        print(key)
        if key == secret_key:
            return secret_values[key]
