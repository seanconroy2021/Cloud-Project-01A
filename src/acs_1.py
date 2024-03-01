import urllib.request
import utils.logger as log
import commandLine.manager as cmd
import ec2.manager as ec2
import s3.manager as s3



userData = """#!/bin/bash
yum update -y
yum install httpd -y
systemctl enable httpd
systemctl start httpd
echo "<html><h1>Hello from ACS</h1></html>" > /var/www/html/index.html

"""

website_configuration = {
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "error.html"},
}

logger = log.setup_logger(name="APP")
def launch_ec2_instance():
    try:
        logger.info("Launching Metadata EC2 Instance...")
        ec2.launch_ec2_instance(
            instanceName="Ec2_Metadata",
            keyName="demo",
            secuirtyGroupId="sg-032fa0004dc0327c2",
            userData=userData,
        )
    except Exception as e:
        logger.error(f"Failed to launch EC2 instance: {e}")


def launch_S3_bucket():
    bucketName=s3.create_s3_bucket("sConroy")
    urllib.request.urlretrieve('https://setuacsresources.s3-eu-west-1.amazonaws.com/image.jpeg', 'data/image.jpeg')
    s3.upload_file_to_bucket(bucketName, "data/image.jpeg", "image/jpeg")
    s3.upload_file_to_bucket(bucketName, "data/index.html", "text/html")
    s3.add_policy(bucketName)
    s3.website_configuration(bucketName, website_configuration)

def launch_monitoring_instance():
        logger.info("Launching Monitoring EC2 Instance...")
        cmd.upload_file(
            key='data/demo.pem',
            ipAddress="54.163.3.93",
            file="data/monitoring.sh"
        )
        cmd.run_command(
            key="data/demo.pem",
            ipAddress="54.163.3.93",
            command='cd ~/script & chmod +x monitoring.sh && ./monitoring.sh'
        )

def main():
    logger = log.setup_logger(name="acs_main")
    logger.info("Starting ACS Project")
    #launch_ec2_instance()
    #launch_S3_bucket()
    launch_monitoring_instance()
    


if __name__ == "__main__":
    main()
    