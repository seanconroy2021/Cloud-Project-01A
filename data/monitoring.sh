#!/usr/bin/bash
#
# Some Updated monitoring functionality
#
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)   
Instance_Public_IP=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)  
Instance_Private_IP=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4) 
Instance_Security_Group=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/security-groups) 

INSTANCE_UP_TIME= uptime -p
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
CPU_USUAGE=$(top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - $1"%"}')
DISK_USUAGE=$(df -h | grep '^/dev' | grep -v 'boot' | awk '{ print $5 " on " $6 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
LOGGED_IN_USERS=$(who)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)
MONGO_PROCESSES=$(ps -A | grep -c mongod)
NETWORK_STATISTICS=$(ss -tuln)
TIME=$(date)
echo "______________________________________"
echo "Meta Data Information"
echo "______________________________________"
echo "Time: $TIME"
echo "Logged in users: $LOGGED_IN_USERS"
echo "Instance Up Time: $INSTANCE_UP_TIME"
echo "Instance ID: $INSTANCE_ID"
echo "Instance Public IP: $Instance_Public_IP"
echo "Instance Private IP: $Instance_Private_IP"
echo "Instance Security Group: $Instance_Security_Group"
echo "______________________________________"
echo "System Information"
echo "______________________________________"
echo "Memory utilisation: $MEMORYUSAGE"
echo "Disk usage: $DISK_USUAGE"
echo "CPU usage: $CPU_USUAGE"
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
echo "Network statistics:"
echo "$NETWORK_STATISTICS"
echo "______________________________________"