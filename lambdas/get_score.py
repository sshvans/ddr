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
table_name = 'ddr_score'
pk = 'pk'


def get_last_score():
    table = dynamodb.Table(table_name)
    db_res = table.query(KeyConditionExpression=Key('score_id').eq('DUMMY'),Limit=1,ScanIndexForward=False)
    return str(db_res['Items'][0]['group_total'])


# Lambda function handler method
def get_score(event, context):
    logger.info('got event {}'.format(event))

    # Get score
    table = dynamodb.Table(table_name)

    fetched_score = get_last_score()
    transformed_score = math.tanh(float(fetched_score) / 1000.0) * 100.0

    logger.debug('score is {}'.format(transformed_score))

    status = {
        'score': transformed_score
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
