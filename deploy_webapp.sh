#! /bin/bash

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