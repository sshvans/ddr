import datetime
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    #print('received event: ' + str(event))
    s3Key = event['Records'][0]['s3']['object']['key']
    print('received S3 Key: ' + str(s3Key))
    file_ts = datetime.datetime.now().isoformat()

    table = dynamodb.Table('ddr_rendered')
    response = table.put_item(
        Item={
            'file_id': 'DUMMY',
            'file_ts': file_ts, #datetime.datetime.now().isoformat(),
            'file_name': s3Key,
            'ttl': int(time.time() + 900)
        }
    )
    # TODO implement
    return