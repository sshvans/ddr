#! /bin/bash
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region)
CF_STACK_ID=$(aws ec2 describe-instances   --instance-id $INSTANCE_ID --region ${REGION} | jq '.[]|.[]|.Instances|.[]|.Tags|.[]|select(.Key == "aws:cloudformation:stack-id")|.Value' | tr -d '"')
DDR_S3_WEBAPP=$(aws cloudformation describe-stacks --stack ${CF_STACK_ID} --region ${REGION} | jq '.[]|.[]|.Outputs|.[]|select(.OutputKey == "S3DdrWebapp")|.OutputValue' | tr -d '"');echo ${DDR_S3_WEBAPP}

python deploy_webapp.py

cd scoreboard-web-app
aws s3 sync . s3://${DDR_S3_WEBAPP}/

for html_file in *.html;
do
git checkout ${html_file}
done

for js_file in *.js;
do
git checkout ${js_file}
done