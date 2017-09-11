import logging
import boto3
from botocore.exceptions import ClientError
import json
import simplejson
import decimal
import math
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
table_name = 'ddr_images'


def get_last_image():
    table = dynamodb.Table(table_name)
    db_res = table.query(KeyConditionExpression=Key('file_id').eq('DUMMY'),Limit=1,ScanIndexForward=False)
    return str(db_res['Items'][0]['file_name'])

# Lambda function handler method
def get_image(event, context):
    logger.info('got event {}'.format(event))

    # Get image
    table = dynamodb.Table(table_name)
    image_file_name = get_last_image()
    tranformed_name = image_file_name.replace(":","_")

    logger.debug('Image file name on s3 bucket is {}'.format(tranformed_name))

    status = {
        'image': tranformed_name
    }

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST"
        },
        "body": json.dumps(status, indent=4, cls=DecimalEncoder)
    }
    return response


class DecimalEncoder(json.JSONEncoder):
    # Helper class to convert a DynamoDB item to JSON.
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
