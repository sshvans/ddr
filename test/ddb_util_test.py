import time

from ddr_server import ddb_util

lek = {}

if not lek:
    r1 = ddb_util.get_first_last_file(True)
    print(r1['files'])
    lek = r1['lastEvaluatedKey']
    print(lek)

last_two_files = ddb_util.get_next_two_files(lek)['files']

while True:
    r = ddb_util.get_next_two_files(lek)

    if len(r['files']) is 2:
        last_two_files = r['files']
#        ddr_score.fetch_score()
    else:
        print("No new file, sleeping 10 seconds")
        time.sleep(1)
        continue

    print(last_two_files)
    lek = {'file_id': 'DUMMY', 'file_ts': r['files'][0]}
    # print(lek)
