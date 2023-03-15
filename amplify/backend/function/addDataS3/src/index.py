import json
import logging
import os

import boto3
from botocore.exceptions import ClientError


def handler(event, context):
  print('received event:')
  print(event)
  
    # Upload the file
  s3_client = boto3.client('s3')
  try:
    s3_client.put_object(Body=json.dumps(event['data']), Bucket='userdatabucket94653-dev', Key='data/data.json')
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': s3_client.generate_presigned_url(
          'get_object',
          Params={'Bucket': 'userdatabucket94653-dev', 'Key': 'data/data.json'},
          ExpiresIn=3600
        )
    }
  except ClientError as e:
      logging.error(e)
      return False