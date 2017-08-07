# DDR

## Up & Running

### Create Key Pair
``` bash
aws ec2 create-key-pair --key-name ddr-pdx --query 'KeyMaterial' --output text > ~/.ssh/ddr-pdx.pem; chmod 600 ~/.ssh/ddr-pdx.pem
```

### Launch Stack & Get InstanceId
``` bash
aws cloudformation create-stack --stack-name ddr --template-body file://cfn_template.yaml; aws cloudformation wait stack-create-complete --stack-name ddr

INSTANCE_ID=$(aws cloudformation describe-stacks --stack-name ddr --query 'Stacks[].Outputs[?OutputKey==`InstanceId`].OutputValue' --output text); echo $INSTANCE_ID
```

### Connect to Instance
``` bash
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids=${INSTANCE_ID} --query 'Reservations[].Instances[0].PublicIpAddress' --output text); echo $PUBLIC_IP

ssh -i ~/.ssh/ddr-pdx.pem ubuntu@${PUBLIC_IP}
```

### Transfer Output
``` bash
scp -i ~/.ssh/ddr-pdx.pem ubuntu@${PUBLIC_IP}:/home/ubuntu/data/output/result.avi .
```

### Play Video Locally
``` bash
open result.avi
```

### Stop Instance
```
INSTANCE_ID=$(aws cloudformation describe-stacks --stack-name ddr --query 'Stacks[].Outputs[?OutputKey==`InstanceId`].OutputValue' --output text); echo $INSTANCE_ID
aws ec2 stop-instances --instance-ids ${INSTANCE_ID}
```
