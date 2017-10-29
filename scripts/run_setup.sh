#! /bin/bash
cd /home/ubuntu/ddr
nohup python -m ddr_server.ddr_runner > /home/ubuntu/ddr_runner.log 2>&1 &
nohup python -m ddr_server.sqs_poller > /home/ubuntu/sqs_poller.log 2>&1 &
cd /home/ubuntu/openpose
nohup ./build/examples/tutorial_pose/op_server.bin > /home/ubuntu/openpose.log 2>&1 &