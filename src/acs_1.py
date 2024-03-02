import urllib.request
import utils.logger as log
import commandLine.manager as cmd
import ec2.manager as ec2
import s3.manager as s3
import utils.openBrowser as browser
import utils.initalStart as start

userData = '''#!/bin/bash
yum update -y
yum install httpd -y
systemctl enable httpd
systemctl start httpd
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
# Start building the HTML content
echo '<!DOCTYPE html>' > index.html
echo '<html>
<head>
    <title>EC2 Instance Information</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { margin: 20px 0; }
        .header { color: #333366; margin: 20px 0; }
        .image { text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <h1 class="header">EC2 Instance Information</h1>' >> index.html

# private ip
echo '<div class="container"> <strong>Private IP Address:</strong> ' >> index.html
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4 >> index.html
echo '</div>' >> index.html

# public ip
echo '<div class="container"> <strong>Public IP Address:</strong> ' >> index.html
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 >> index.html
echo '</div>' >> index.html

# instance id
echo '<div class="container"> <strong>Instance ID:</strong> ' >> index.html
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id >> index.html
echo '</div>' >> index.html

# instance type
echo '<div class="container"> <strong>Instance Type:</strong> ' >> index.html
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-type >> index.html
echo '</div>' >> index.html

# availability zone
echo '<div class="container"> <strong>Availability Zone:</strong> ' >> index.html
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone >> index.html
echo '</div>' >> index.html

# ami id
echo '<div class="container">
        <strong>AMI ID:</strong> ' >> index.html
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/ami-id >> index.html
echo '</div>' >> index.html

# image 
echo '<div class="image">
        <img src="https://miro.medium.com/v2/resize:fit:720/1*icemCezVMahlyIQB31tzpA.png" alt="EC2 Image" style="width:50%;">
    </div>
</body>
</html>' >> index.html
cp index.html /var/www/html/index.html
'''
userDatabase = '''#!/bin/bash
sudo yum update -y

echo '[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc' > /etc/yum.repos.d/mongodb-org-7.0.repo

yum install -y mongodb-org
sleep 30

systemctl enable mongod
systemctl start mongod

sleep 30

TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PUBLIC_DNS_NAME=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-hostname)
sed -i "s/bindIp: 127.0.0.1/bindIp: $PUBLIC_DNS_NAME/" /etc/mongod.conf
systemctl restart mongod
'''

websiteConfiguration = {
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "error.html"},
}

logger = log.setup_logger(name="APP")
def launch_monitoring_instance_metadata(ip,keyName):
        logger.info("Launching Monitoring EC2 Instance MetaData...")
        cmd.upload_file(
            key=f'data/{keyName}.pem',
            ipAddress=ip,
            file="data/monitoring.sh"
        )
        cmd.run_command(
            key=f'data/{keyName}.pem',
            ipAddress=ip,
            command='chmod +x monitoring.sh && ./monitoring.sh'
        )

def add_data_to_database(ip, dns,keyName):
    logger.info("Adding data to Database...")
    cmd.upload_file(
        key=f'data/{keyName}.pem',
        ipAddress=ip,
        file="data/database.json"
    )
    command = f"mongoimport --host {dns} --db irelandCounties --collection counties --file database.json --jsonArray"
    cmd.run_command(
        key=f'data/{keyName}.pem',
        ipAddress=ip,
        command=command
    )

def launch_ec2_instance_DataBase(secuirtyGroupId, keyName):
    try:
        logger.info("Launching Database EC2 Instance...")
        ip,dns =ec2.launch_ec2_instance(
            instanceName="Ec2_Database(ACS)",
            keyName=keyName,
            secuirtyGroupId=secuirtyGroupId,
            userData=userDatabase,
        )
        browser.wait_for_url(f"http://{dns}:27017", 120, 60)
        add_data_to_database(ip, dns,keyName)
    except Exception as e:
        logger.error(f"Failed to launch EC2 instance: {e}")

def launch_ec2_instance(secuirtyGroupId, keyName):
    try:
        logger.info("Launching Metadata EC2 Instance...")
        ip,dns=ec2.launch_ec2_instance(
            instanceName="Ec2_Metadata(ACS)",
            keyName=keyName,
            secuirtyGroupId=secuirtyGroupId,
            userData=userData,
        )
        browser.open_browser("Metadata Website", f"http://{ip}")
        launch_monitoring_instance_metadata(ip,keyName)
    except Exception as e:
        logger.error(f"Failed to launch EC2 instance: {e}")

def launch_S3_bucket():
    bucketName=s3.create_s3_bucket("ScronoyBucket")
    urllib.request.urlretrieve('https://setuacsresources.s3-eu-west-1.amazonaws.com/image.jpeg', 'data/image.jpeg')
    s3.upload_file_to_bucket(bucketName, "data/image.jpeg", "image/jpeg")
    s3.upload_file_to_bucket(bucketName, "data/index.html", "text/html")
    s3.add_policy(bucketName)
    s3.website_configuration(bucketName, websiteConfiguration)
    browser.open_browser("S3 Website", f"http://{bucketName}.s3-website-us-east-1.amazonaws.com")

def main():
    logger = log.setup_logger(name="Runner")
    logger.info("Starting Sean Conroy ACS Project")
    secuirtyGroupId, keyName =start.setup()
    launch_ec2_instance(secuirtyGroupId,keyName)
    launch_ec2_instance_DataBase(secuirtyGroupId,keyName)
    # launch_S3_bucket()
    logger.info("ACS Project Completed")
    
if __name__ == "__main__":
    main()
    