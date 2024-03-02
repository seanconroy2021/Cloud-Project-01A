import urllib.request
import utils.logger as log
import commandLine.manager as cmd
import ec2.manager as ec2
import s3.manager as s3
import utils.openBrowser as browser


#echo "<html><h1>Hello from ACS</h1></html>" > /var/www/html/index.html
userData = """#!/bin/bash
yum update -y
yum install httpd -y
systemctl enable httpd
systemctl start httpd



"""

userDatabase = """#!/bin/bash
yum update -y
echo "[mongodb-org-4.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/4.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc" > /etc/yum.repos.d/mongodb-org-4.4.repo
yum install -y mongodb-org
systemctl start mongod
systemctl enable mongod
"""

website_configuration = {
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "error.html"},
}

logger = log.setup_logger(name="APP")
def launch_monitoring_instance(ip):
        logger.info("Launching Monitoring EC2 Instance...")
        cmd.upload_file(
            key='data/demo.pem',
            ipAddress=ip,
            file="data/monitoring.sh"
        )
        cmd.run_command(
            key="data/demo.pem",
            ipAddress=ip,
            command='cd ~/script & chmod +x monitoring.sh && ./monitoring.sh'
        )

def launch_ec2_instance_DataBase():
    try:
        logger.info("Launching Database EC2 Instance...")
        response=ec2.launch_ec2_instance(
            instanceName="Ec2_Database(ACS)",
            keyName="demo",
            secuirtyGroupId="sg-032fa0004dc0327c2",
            userData=userDatabase,
        )
        ip = response
        launch_monitoring_instance(ip)
    except Exception as e:
        logger.error(f"Failed to launch EC2 instance: {e}")
def launch_ec2_instance():
    try:
        logger.info("Launching Metadata EC2 Instance...")
        response=ec2.launch_ec2_instance(
            instanceName="Ec2_Metadata(ACS)",
            keyName="demo",
            secuirtyGroupId="sg-032fa0004dc0327c2",
            userData=userData,
        )
        ip = response
        browser.open_browser("Metadata Website", f"http://{ip}")
        launch_monitoring_instance(ip)
    except Exception as e:
        logger.error(f"Failed to launch EC2 instance: {e}")


def launch_S3_bucket():
    bucketName=s3.create_s3_bucket("sConroy")
    urllib.request.urlretrieve('https://setuacsresources.s3-eu-west-1.amazonaws.com/image.jpeg', 'data/image.jpeg')
    s3.upload_file_to_bucket(bucketName, "data/image.jpeg", "image/jpeg")
    s3.upload_file_to_bucket(bucketName, "data/index.html", "text/html")
    s3.add_policy(bucketName)
    s3.website_configuration(bucketName, website_configuration)
    browser.open_browser("S3 Website", f"http://{bucketName}.s3-website-us-east-1.amazonaws.com")

def main():
    logger = log.setup_logger(name="acs_main")
    logger.info("Starting ACS Project")
    # launch_ec2_instance()
    launch_ec2_instance_DataBase()
    # launch_S3_bucket()
    
    
    


if __name__ == "__main__":
    main()
    