# DDR

![DDR Architecture](/images/ddr_architecture_diagram.png?raw=true "DDR Architecture")

## Pre-requisites

This project uses Amazon Rekognition and can be run in one of three regions:
* US East (N. Virginia)
* US West (Oregon)
* EU (Ireland)

3 Lambda functions with Python 3.6 runtime are deployed as part of this project. 
The scripts are located in lambdas directory.

A cloudformation template: `ddr.template` has been provided to automate the server side infrastructure. 
The lambda scripts are uploaded as zip files and can be sourced only from S3 buckets in the same region.

### [Optional] Create or re-use a key pair
You can re-use a pre-existing key pair in the region if you already have one. Command to generate a key pair is below.
``` bash
aws ec2 create-key-pair --key-name ddr-pdx --query 'KeyMaterial' --output text > ~/.ssh/ddr-pdx.pem; chmod 600 ~/.ssh/ddr-pdx.pem
```

## Up & Running
A helper script `deploy_lambda_cfn.sh` has been provided to automate the server setup. See testing.md for individual steps. 
The script expects three arguments, in this order: 
* `region`: has to be one of `us-east-1`, `us-west-2`, `eu-west-1`
* `key_name`: name of existing imported key pair in the chosen region
* `lambda_assets_bucket`: name of a new bucket to host lambda assets 

The script creates the above named buckets, hosts all lambda assets in the bucket and then launches ddr.template cloudformation stack
taking `ddr_test_params.json` file as input. The file contains three tokens for VPCID, KeyName, ArtifactBucket. The script chooses your default VPC
and uses input values for the other two parameters. Please also note that it grants access from anywhere by having 0.0.0.0/0 in the RemoteAccessCIDR parameter.
This is strictly for demo purpose and you should change this value to your IP for security. The parameters file can be modified to match your environment.

### Run the deploy script
```bash
./deploy_lambda_cfn.sh <aws_region> <key_name> <new_assets_bucket>
# e.g. ./deploy_lambda_cfn.sh us-east-1 ddr-pdx my-ddr-assets-bucket
```

### Run scripts on server
1. After the above script has finished. Use the console or CLI to get the public ip of the instance launched. Substitute STACK_ID and REGION below.

```
   aws cloudformation describe-stacks --stack ${STACK_ID} --region ${REGION} \
   | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "DdrEC2PublicIp")|.OutputValue'
```

2. SSH to the EC2 server with the IP identified above
`ssh -i ddr-pdx.pem ubuntu@<34.236.149.123-REPLACE_THIS>`

3. Execute setup script and run server process
* setup_bucket_notifications.sh - sets up notification events for s3 bucket and prepares ddr_config.props
* run_server.sh runs three processes: 
  * sqs_poller - Processes incoming files on S3 notified to SQS
  * ddr_runner - computes scores and runs rekognition commands
  * op_server - Openpose server running zeromq endpoint. Listens on incoming requests and processes images
```bash
   cd ~/ddr
   git pull
   cd scripts
   ./setup_bucket_notifications.sh
   ./run_server.sh
```

4. Deploy webapp to created s3 webapp bucket
```bash
   cd ~/ddr
   ./deploy_webapp.sh
```

## Raspberry PI
* Follow instructions in ddr_raspi/README.md
* It will create a S3 bucket
* See instructions in section: *Run ddr_camera.py*

## Final Testing
Ensure the following:
* `ddr_camera` is running on raspberry pi
* `run_server.sh` has been executed on openpose EC2 instance
  * `ps -ef | grep python` and `ps -ef | grep op_server` should list the processes
  e.g.
      ```bash
      ubuntu@ip-172-31-9-99:~/ddr$ ps -ef | grep python
      ubuntu    2861     1  0 02:34 pts/1    00:00:35 python -m ddr_server.ddr_runner
      ubuntu    2862     1 16 02:34 pts/1    00:23:10 python -m ddr_server.sqs_poller
      ubuntu    3383  3282  0 04:56 pts/0    00:00:00 grep --color=auto python
      ubuntu@ip-172-31-9-99:~/ddr$ ps -ef | grep op_server
      ubuntu    2863     1  0 02:34 pts/1    00:00:06 ./build/examples/tutorial_pose/op_server.bin
      ubuntu    3385  3282  0 04:56 pts/0    00:00:00 grep --color=auto op_server
      ```
 
* Verify scores on the S3 website. Substitute bucket name and region.
  * Image: e.g. http://ddr-stack-20171028-220958-s3ddrwebapp-rvsrxjt4l0e.s3-website-us-east-1.amazonaws.com/images.html
  * Score: e.g. http://ddr-stack-20171028-220958-s3ddrwebapp-rvsrxjt4l0e.s3-website-us-east-1.amazonaws.com/scoreboard_v2_save_last.html
  
* Inspecting the API Gateway output. Substitute endpoint and region in the url below
  * Score: e.g. https://as8oin2dc6.execute-api.us-east-1.amazonaws.com/prod/score?lek=null
  * Image: e.g. https://as8oin2dc6.execute-api.us-east-1.amazonaws.com/prod/image?lek=null
  
