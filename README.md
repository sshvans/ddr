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

## Processing Images

### Make directories to hold images and processed images
``` bash
ssh -i ~/.ssh/ddr-pdx.pem ubuntu@${PUBLIC_IP}
mkdir images processed
```

### Upload test images from local
``` bash
LOCAL_IMAGE_DIR=/path/to/your/test/images/dir
scp -i ~/.ssh/ddr-pdx.pem -r ${LOCAL_IMAGE_DIR}/* ubuntu@${PUBLIC_IP}:~/images/
```

### Process test images on EC2
``` bash
ssh -i ~/.ssh/ddr-pdx.pem ubuntu@${PUBLIC_IP}
cd ~/openpose
# JSON Output:
./build/examples/openpose/openpose.bin --image_dir ~/images --write_keypoint_json ~/processed/ --no_display
# Rendered images:
./build/examples/openpose/openpose.bin --image_dir ~/images --write_images ~/processed/ --no_display
```

### View rendered images locally
``` bash
scp -i ~/.ssh/ddr-pdx.pem ubuntu@${PUBLIC_IP}:~/processed/* .
open *.png
```
