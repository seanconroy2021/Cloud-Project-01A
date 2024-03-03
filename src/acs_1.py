import urllib.request

import commandLine.manager as cmd
import ec2.manager as ec2
import s3.manager as s3
import utils.initalStart as start
import utils.logger as log
import utils.openBrowser as browser

userData = """#!/bin/bash
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

#image
echo '<div class="image">
        <img src="https://miro.medium.com/v2/resize:fit:720/1*icemCezVMahlyIQB31tzpA.png" alt="EC2 Image" style="width:50%;">
    </div>
</body>
</html>' >> index.html
cp index.html /var/www/html/index.html
"""
# link:https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-amazon/
# link:https://docs.aws.amazon.com/dms/latest/sbs/chap-mongodb2documentdb.02.html
userDatabase = """#!/bin/bash
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
"""
websiteConfiguration = {
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "error.html"},
}

logger = log.setup_logger(name="APP")


# This function uses helper functions created in the ec2.manager.py and commandLine.manager.py files.
def launch_monitoring_instance_script(ip, keyName,name):
    """
    This function is used to launch the monitoring instance metadata.
    it take in the ip address and the key name and name of the instance.
    """
    logger.info(f"Launching Monitoring EC2 Instance {name}...")
    cmd.upload_file(key=f"data/{keyName}.pem", ipAddress=ip, file="data/monitoring.sh")
    cmd.run_command(
        key=f"data/{keyName}.pem",
        ipAddress=ip,
        command="chmod +x monitoring.sh && ./monitoring.sh",
    )


# This function uses helper functions created in the commandLine.manager.py
# It will SCP and SSH into the EC2 instance and upload the database.json file to the EC2 instance.
# Then it will run the mongoimport command to add the data to the database.
def add_data_to_database(ip, dns, keyName):
    """
    This function is used to add data to the database.
    It takes in the ip address, dns and key name.
    Ip is needed for the SSH connection and the dns is needed for the mongoimport command.
    The Data is added from the data/database.json file.
    """
    logger.info("Adding data to Database...")
    cmd.upload_file(key=f"data/{keyName}.pem", ipAddress=ip, file="data/database.json")
    command = f"mongoimport --host {dns} --db irelandCounties --collection counties --file database.json --jsonArray"
    cmd.run_command(key=f"data/{keyName}.pem", ipAddress=ip, command=command)


# This function uses helper functions created in the ec2.manager.py, rowser.manager.py and launch_monitoring_instance_metadata.
# It will launch the EC2 instance and use the user data to install mongoDB and start the mongoDB service.
# Then open a browser to the EC2 instance after it is accessible also write the URL to a data/url.txt (note: mongoDB will say It looks like you are trying to access MongoDB over HTTP on the native driver port. ).
# Lastly it will launch the monitoring instance metadata which outputs the instance information to the logs. (note: That a web server will not be running only mongoDB)
def launch_ec2_instance_DataBase(secuirtyGroupId, keyName):
    """
    This function is used to launch the database EC2 instance.
    It takes in the security group id and the key name.
    It then will open a browser to the database link to check it accessible.

    The function also run a local command that will use the mongo shell to print the data in the database to the logs.
     also it will run launch the monitoring instance metadata which outputs the instance information to the logs.
    """
    try:
        logger.info("Launching Database EC2 Instance...")
        ip, dns = ec2.launch_ec2_instance(
            instanceName="Ec2_Database(ACS)",
            keyName=keyName,
            secuirtyGroupId=secuirtyGroupId,
            userData=userDatabase,
        )
        browser.open_browser("Datbase Link", f"http://{dns}:27017")
        add_data_to_database(ip, dns, keyName)
        command = f'mongosh "mongodb://{dns}/irelandCounties" --eval "printjson(db.counties.find().toArray())"'
        cmd.run_local_command(command)
        launch_monitoring_instance_script(ip, keyName,"Database")
    except Exception:
        logger.error("Failed to fully launch EC2 Database")
        logger.warning("Skipping the rest of this function.....")
        return


# This function uses helper functions created in the ec2.manager.py, browser.manager.py and launch_monitoring_instance_metadata.
# It will launch the EC2 instance and user user data to install httpd and start the httpd service.
# User data will also be used to get the instance information from metadata  and write it to a index.html file.
# Then function will open a browser to the EC2 instance after it is accessible also write the URL to a data/url.txt.
# Lastly it will launch the monitoring instance metadata which outputs the instance information to the logs. (note: That a web server will be running)
def launch_ec2_instance(secuirtyGroupId, keyName):
    """
    This function is used to launch the metadata EC2 instance.
    It will run user data to install httpd and start the httpd service plus get the instance information from metadata output to index.html.
    It takes in the security group id and the key name.
    """
    try:
        logger.info(f"Launching Metadata EC2 Instance...")
        ip, dns = ec2.launch_ec2_instance(
            instanceName="Ec2_Metadata(ACS)",
            keyName=keyName,
            secuirtyGroupId=secuirtyGroupId,
            userData=userData,
        )
        browser.open_browser("Metadata Website", f"http://{ip}")
        launch_monitoring_instance_script(ip, keyName,"Metadata")
    except Exception:
        logger.error("Failed to fully launch EC2 Metadata")
        logger.warning("Skipping the rest of this function.....")
        return

def get_image():  
    """
    This function is used to get the image from a S3 bucket.
    If the image cannot be retrieved it will raise an exception.
    """      
    try:
        logger.info("Getting Image.....")
        urllib.request.urlretrieve(
                "https://setuacsresources.s3-eu-west-1.amazonaws.com/image.jpeg",
                "data/image.jpeg",
            )
    except Exception:
        logger.error("Failed to get image")
        raise Exception("Failed to get image")

# This function uses helper functions created in the s3.manager.py and browser.manager.py.
# It will create a S3 bucket and add attributes to indexTemplate.html (name and url) and upload it to the S3 bucket.
# It will also upload the image.jpeg the S3 bucket after retrieving it from the the other S3 bucket.
# Then it will add a policy (pre-set) to the S3 bucket and add the website configuration to the S3 bucket.
# Lastly it will open a browser to the S3 bucket after it is accessible and output the URL to data/url.txt.

def launch_S3_bucket():
    """
    This function is used to launch the S3 bucket.
    It will create a S3 bucket and add attributes to indexTemplate.html (name and url) and upload it to the S3 bucket.
    It will also upload the image.jpeg the S3 bucket after retrieving it from the the other S3 bucket.
    Then it will add a policy (pre-set) to the S3 bucket and add the website configuration to the S3 bucket.
    lastly open a browser to the S3 bucket after it is accessible and output the URL to data/url.txt.
    """
    try:

        logger.info("Launching S3 Bucket...")
        get_image()
        bucketName, regoin = s3.create_s3_bucket("ScronoyBucket")
        url = f"http://{bucketName}.s3-website-{regoin}.amazonaws.com"
        with open("data/indexTemplate.html", "r") as file:
            html = file.read()
        newHtml = html.replace("{name}", bucketName).replace("{URL}", url)
        with open("data/index.html", "w") as newFile:
            newFile.write(newHtml)
        s3.upload_file_to_bucket(bucketName, "data/image.jpeg", "image/jpeg")
        s3.upload_file_to_bucket(bucketName, "data/index.html", "text/html")
        s3.add_policy(bucketName)
        s3.website_configuration(bucketName, websiteConfiguration)
        browser.open_browser("S3 Website", url)
    except Exception:
        logger.error("Failed to fully launch S3 website")
        logger.warning("Skipping the rest of this function.....")
        return

def before_exit():
    logger.info("ACS Project Completed")
    logger.info("Exiting Program")
    logger.info("Log can be found in the data/logs folder")


def main():
    logger = log.setup_logger(name="Main")
    logger.info("Starting Sean Conroy ACS Project")
    secuirtyGroupId, keyName = start.setup()
    launch_ec2_instance(secuirtyGroupId, keyName)
    launch_ec2_instance_DataBase(secuirtyGroupId, keyName)
    launch_S3_bucket()
    before_exit()

if __name__ == "__main__":
    main()
