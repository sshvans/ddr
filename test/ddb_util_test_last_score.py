from ddr_server import ddb_util
from boto3.dynamodb.conditions import Key, Attr


last_score = {'score': None, 'lastEvaluatedKey': None}
res = ddb_util.get_last_score(last_score)
print(res)

table = ddb_util.dynamodb.Table(ddb_util.score_table)
db_res = table.query(KeyConditionExpression=Key('score_id').eq('DUMMY'),Limit=1,ScanIndexForward=False)
print(db_res)

while True:
    score = ddb_util.get_last_score(last_score)
    lek = score['lastEvaluatedKey']
    print(score['score'])