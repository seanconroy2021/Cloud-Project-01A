#!/usr/bin/bash
#
# Some basic monitoring functionality; Tested on Amazon Linux 2.
#
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_UP_TIME=
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)
MONGO_PROCESSES=$(ps -A | grep -c mongod)
TIME=$(date)

echo "Time: $TIME"
echo "Instance ID: $INSTANCE_ID"
echo "Memory utilisation: $MEMORYUSAGE"
echo "No of processes: $PROCESSES"
if [ $HTTPD_PROCESSES -ge 1 ]
then
    echo "Web server is running"
else
    echo "Web server is NOT running"
fi

if [ $MONGO_PROCESSES -ge 1 ]
then
    echo "MongoDB is running."
else
    echo "MongoDB is NOT running."
fi