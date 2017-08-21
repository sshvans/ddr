import time
import os
import subprocess

from ddr_server import ddb_util
from ddr_server import ddr_score

lek = {}

if not lek:
    r1 = ddb_util.get_first_last_file(False)
    print(r1['files'])
    lek = r1['lastEvaluatedKey']
    print(lek)

last_two_files = ddb_util.get_next_two_files(lek)['files']

while True:
    r = ddb_util.get_next_two_files(lek)

    if len(r['files']) is 2:
        subprocess.call(os.path.expanduser('~') + '/' + 'openpose.sh')
        last_two_files = r['files']
        file1 = os.path.expanduser('~') + '/archived/' + 'image' + str(last_two_files[0]).replace(':','_') + '_keypoints.json'
        file2 = os.path.expanduser('~') + '/archived/' + 'image' + str(last_two_files[1]).replace(':','_') + '_keypoints.json'
        group_score = ddr_score.fetch_score(file1, file2)
        ddb_util.put_score(group_score)

        last_score = ddb_util.get_last_score()
        print("LAST SCORE: " + last_score)

    else:
        print("No new file, sleeping 1 seconds")
        time.sleep(1)
        continue

    print(last_two_files)
    lek = {'file_id': 'DUMMY', 'file_ts': r['files'][0]}
    # print(lek)
