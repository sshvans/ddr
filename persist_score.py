import boto3
import json
import decimal
import datetime
from boto3.dynamodb.conditions import Key, Attr


class DecimalEncoder(json.JSONEncoder):
    # Helper class to convert a DynamoDB item to JSON.
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
ddbclient = boto3.client('dynamodb')
score_table = 'ddr_score'
images_table = 'ddr_images'


def create_table(table_name, partition_key, sort_key):
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': partition_key, #'score_id',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': sort_key, #'score_ts',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': partition_key, #'score_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': sort_key, #'score_ts',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    print("Table status:", table.table_status)


def check_or_create_table(table_name, partition_key, sort_key):
    try:
        response = ddbclient.describe_table(TableName = table_name)
    except:
        print("Table does not exist, creating...")
        create_table(table_name, partition_key, sort_key)


def setup_ddb_tables():
    check_or_create_table(score_table, 'score_id', 'score_ts')
    check_or_create_table(images_table, 'file_id', 'file_ts')


def put_item(score_result):
    #[average group score, total group score, number of people, array of individual scores]
    people_scores = [decimal.Decimal(str(x)) for x in score_result[3]]
    table = dynamodb.Table(score_table)
    response = table.put_item(
        Item={
            'score_id': 'DUMMY',
            'score_ts': datetime.datetime.now().isoformat(),
            'group_avg': decimal.Decimal(str(score_result[0])),
            'group_total': decimal.Decimal(str(score_result[1])),
            'num_people': decimal.Decimal(str(score_result[2])),
            'people_scores': people_scores
        }
    )

    print("PutItem succeeded")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))


def get_last_score():
    table = dynamodb.Table(score_table)
    db_res = table.query(KeyConditionExpression=Key('score_id').eq('DUMMY'),Limit=1,ScanIndexForward=False)
    return str(db_res['Items'][0]['group_avg'])


