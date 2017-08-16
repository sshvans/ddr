import logging
import boto3
from botocore.exceptions import ClientError
import json
import simplejson
import decimal

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
table_name = 'ddr_score'
pk = 'pk'

# Lambda function handler method
def get_score(event, context):
    logger.info('got event {}'.format(event))

    # Get score
    table = dynamodb.Table(table_name)

    itemObj = table.get_item(
        Key={
            'pk': pk
        },
        AttributesToGet=[
            'score'
        ]
    )
    logger.debug('score is {}'.format(itemObj['Item']))

    status = {
        'score': itemObj['Item']['score']
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
