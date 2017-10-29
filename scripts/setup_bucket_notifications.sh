#! /bin/bash
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region)
CF_STACK_ID=$(aws ec2 describe-instances   --instance-id $INSTANCE_ID --region ${REGION} | jq '.[]|.[]|.Instances|.[]|.Tags|.[]|select(.Key == "aws:cloudformation:stack-id")|.Value' | tr -d '"')
DDR_FUNCTION_ARN=$(aws cloudformation describe-stacks --stack ${CF_STACK_ID} --region ${REGION} | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "DdrS3RenderedFunctionARN")|.OutputValue' | tr -d '"')
DDR_S3_RESOURCE=$(aws cloudformation describe-stacks --stack ${CF_STACK_ID} --region ${REGION} | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "S3DdrResources")|.OutputValue' | tr -d '"')
QUEUE_ARN=$(aws cloudformation describe-stacks --stack ${CF_STACK_ID} --region ${REGION} | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "DdrMessagesQueueARN")|.OutputValue' | tr -d '"')
SQS_URL=$(aws cloudformation describe-stacks --stack ${CF_STACK_ID} --region ${REGION} | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "DdrMessagesQueue")|.OutputValue' | tr -d '"')
API_ID=$(aws cloudformation describe-stacks --stack ${CF_STACK_ID} --region ${REGION} | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "DdrApi")|.OutputValue' | tr -d '"');echo ${API_ID}
DDR_S3_WEBAPP=$(aws cloudformation describe-stacks --stack ${CF_STACK_ID} --region ${REGION} | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "S3DdrWebapp")|.OutputValue' | tr -d '"');echo ${DDR_S3_WEBAPP}
aws lambda add-permission --function-name ${DDR_FUNCTION_ARN} --statement-id allow-s3-lambda-invoke-ddr --action "lambda:InvokeFunction" --principal s3.amazonaws.com --source-arn "arn:aws:s3:::${DDR_S3_RESOURCE}" --region ${REGION}

sed -i "s/DDR_FUNCTION_ARN/${DDR_FUNCTION_ARN}/g" lambda_notification.json
sed -i "s/QUEUE_ARN/${QUEUE_ARN}/g" lambda_notification.json
aws s3api put-bucket-notification-configuration --region ${REGION} --bucket ${DDR_S3_RESOURCE} --notification-configuration file://lambda_notification.json

git pull
cp /tmp/ddr_config.props /home/ubuntu/ddr/ddr_config.props


