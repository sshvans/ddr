import time
import os
import subprocess
import sys
import traceback

from ddr_server import ddb_util
from ddr_server import ddr_score


def initialize_last_key():
    # The while loop is for the case where raspberry pi has not put any images in S3 yet,
    # hence the dynamodb table storing file names is empty
    lek = {}
    while not lek:
        try:
            r1 = ddb_util.get_first_last_file(False)
            lek = r1['lastEvaluatedKey']
        except:
            time.sleep(0.1)
            lek = {}
    return lek


def openpose_process():
    lek = initialize_last_key()
    print("Obtained lek: " + str(lek))
    while True:
        try:
            r = ddb_util.get_next_two_files(lek)
            last_two_files = r['files']
            if len(r['files']) is 2:
                print("Starting sub process ")
                subprocess.call(os.path.expanduser('~') + '/' + 'openpose.sh')
                last_two_files = r['files']
                file1 = os.path.expanduser('~') + '/archived/' + 'image' + str(last_two_files[0]).replace(':','_') + '_keypoints.json'
                file2 = os.path.expanduser('~') + '/archived/' + 'image' + str(last_two_files[1]).replace(':','_') + '_keypoints.json'

                while True:
                    if os.path.isfile(file1) and os.path.isfile(file2):
                        group_score = ddr_score.fetch_score(file1, file2)
                        break
                    else:
                        time.sleep(2)
                        subprocess.call(os.path.expanduser('~') + '/' + 'openpose.sh')

                ddb_util.put_score(group_score)

            else:
                print("No new file, sleeping 1 seconds")
                time.sleep(1)
                continue

            print(last_two_files)
            lek = {'file_id': 'DUMMY', 'file_ts': r['files'][0]}

        except:
            print("Error occurred in main server loop")
            traceback.print_exc()
            time.sleep(1)


def main(argv):
    ddb_util.setup_ddb_tables()
    openpose_process()


if __name__ == '__main__':
    main(sys.argv[1:])
