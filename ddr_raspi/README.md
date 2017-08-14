# ddr_raspi

## Prerequisites

### Provision Hardware
The following hardware was used:

- MacBook Pro with SD Card slot
- Raspberry Pi 3 Model B
- Raspberry Pi Camera V2
- 2.5A Power Supply for Raspberry Pi
- SanDisk Ultra 16 GB microSDHC UHS-I Card w/ Adapter

### Create AWS Resources

```
macos$ aws cloudformation create-stack --stack-name ddr-raspi --template-body file://ddr_raspi.yaml --capabilities CAPABILITY_NAMED_IAM; aws cloudformation wait stack-create-complete --stack-name ddr-raspi
```

### Create Access Keys
*Note: Record AccessKeyId and SecretAccessKey so you can use them later when configuring AWS credentials on the Raspberry Pi*

```
RASPI_USER=$(aws cloudformation describe-stacks --stack-name ddr-raspi --query 'Stacks[].Outputs[?OutputKey==`User`].OutputValue' --output text); echo $RASPI_USER
macos$ aws iam create-access-key --user-name ${RASPI_USER}
```

### Create Properties File (ddr_camera.props)
```
macos$ IMAGE_BUCKET=$(aws cloudformation describe-stacks --stack-name ddr-raspi --query 'Stacks[].Outputs[?OutputKey==`Bucket`].OutputValue' --output text); echo $IMAGE_BUCKET
macos$ echo "s3_bucket: ${IMAGE_BUCKET}" | tee ddr_camera.props
```


## Install Raspbian on microSD Card

### Insert SD Card into Mac
- Manual Step

### Download OS (Raspbian Jessie Lite)
*Note: This step make take a while*
```
macos$ curl -O http://vx2-downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2017-07-05/2017-07-05-raspbian-jessie-lite.zip
```

### Unzip Archive
```
macos$ tar -xvf 2017-07-05-raspbian-jessie-lite.zip
```

### Identify Mount Point
```
macos$ SD_FILESYSTEM=$(df -h | grep '/Volumes/NO NAME' | awk '{print $1}'); echo $SD_FILESYSTEM
```

### Unmount Volume
```
macos$ sudo diskutil unmount ${SD_FILESYSTEM}
``` 

### Convert and Copy Image to SD Card
*Note: This step make take a while*
```
macos$ sudo dd bs=1m if=./2017-07-05-raspbian-jessie-lite.img of=/dev/rdisk2
```
### Create SSH File
```
macos$ touch /Volumes/boot/ssh
```

### Eject SD Card
```
macos$ sudo diskutil eject /dev/rdisk2
```


## Set Physical Connections
- Insert microsSD Card to "Raspberry Pi 3 Model B"
- Connect "Raspberry Pi Camera V2" to "Raspberry Pi 3 Model B"
- Connect "Raspberry Pi 3 Model B" to Mac via ethernet cable
- Connect "2.5A Power Supply for Raspberry Pi" to "Raspberry Pi Model B"

## Configure Raspberry Pi
### Create SSH Keys
```
macos$ ssh-keygen -t rsa -C ddr@pi -f ~/.ssh/ddr_pi -P ''
```

### Find IP Address for Raspberry Pi and Set As Env Variable
```
macos$ RASPI_IP=$(ping -c 1 raspberrypi.local | grep 'bytes from' | awk '{print $4}' | tr -d :)
```

### Copy Public Key to Raspberry Pi
```
macos$ cat ~/.ssh/ddr_pi.pub | ssh pi@${RASPI_IP} 'install -d -m 700 ~/.ssh;cat >> .ssh/authorized_keys;'
```

### SSH to Raspberry Pi
```
macos$ ssh -i ~/.ssh/ddr_pi pi@${RASPI_IP}
```

### Start raspi-config 
- Change User Password
- Interfacing Options > P1 Camera : Enable
- Advanced Options > Expand Filesystem
- Reboot when prompted

```
raspi$ sudo raspi-config
```

### SSH to Raspberry Pi
```
macos$ ssh -i ~/.ssh/ddr_pi pi@${RASPI_IP}
```

### Check Available Wireless Networks
```
raspi$ sudo iwlist wlan0 scan | grep ESSID
```

### Add Entry to /etc/wpa_supplicant/wpa_supplicant.conf
```
network={
  ssid="<your_ssid>"
  psk="<your_wifi_password>"
}
```

### Restart Wireless
```
raspi$ sudo ifdown wlan0
raspi$ sudo ifup wlan0
```

### Disconnect Ethernet Cable
- Manual

### SSH to Raspberry Pi

```
macos$ ssh -i ~/.ssh/ddr_pi pi@${RASPI_IP}
```

### Apply Updates
```
raspi$ sudo apt-get update -y
raspi$ sudo apt-get install python-picamera -y
raspi$ sudo apt-get install python-pip -y
raspi$ sudo apt-get dist-upgrade -y
```

### Install AWS CLI and Boto3
```
raspi$ sudo pip install awscli boto3
```

### Configure Access
```
raspi$ aws configure
```

## Deploy ddr_camera.py and ddr_camera.props
```
raspi$ exit
macos$ scp -i ~/.ssh/ddr_pi -r ddr_camera.* pi@${RASPI_IP}:.
macos$ ssh -i ~/.ssh/ddr_pi pi@${RASPI_IP} 'chmod +x ddr_camera.py; mkdir images;'
```

### Run ddr_camera.py
```
macos$ ssh -i ~/.ssh/ddr_pi pi@${RASPI_IP}
raspi$ ./ddr_camera.py
```

## Troubleshooting

### Check Camera Connection
```
raspi$ vcgencmd get_camera
```

### Restart
```
raspi$ sudo shutdown –r
```

### Shutdown Raspberry Pi
```
raspi$ sudo shutdown -h now
```

## Resources
- https://www.raspberrypi.org/learning/getting-started-with-picamera/worksheet/
