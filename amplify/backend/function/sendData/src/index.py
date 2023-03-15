import json

import boto3

secretmanager = boto3.client('secretsmanager')
lambdaEvent = boto3.client('lambda')


def handler(event, context):
    print('received event:')
    print(event)
    
    if event['body']['token']:
        token = event['body']['token']
        user_id = get_user_id_in_secret("userSecret", token)
        data_from_body = event['body']['data']
        payload = {
            'data': data_from_body,
            'userId': user_id
        }
        if event['body']['action'] == 'DB':
            lambdaEvent.invoke(
                FunctionName='amplifyaddUser',
                InvocationType='Event',
                Payload=payload,
            )
    return {
        'statusCode': 405,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Pas de TOKEN envoyé')
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
        if secret_values[key] == secret_key:
            return key
