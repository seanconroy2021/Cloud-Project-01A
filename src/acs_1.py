import urllib.request
import utils.logger as log
import ec2.manager as ec2
import s3.manager as s3
import utils.logger as log
out= "#!/bin/bash\n echo 'test' > /tmp/hello \n echo'Hello World' > /var/hello.txtl\n"
user_data =""" #!/bin/bash
# Use this for your user data (script from top to bottom)
# install httpd (Linux 2 version)
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
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
            instanceName="worknowplease",
            keyName="Sean_Ec2",
            secuirtyGroupId="sg-0e5f28f401d119a5a",
            userData=user_data,
        )
    except Exception as e:
        logger.error(f"Failed to launch EC2 instance: {e}")


def launch_S3_bucket():
    bucketName =s3.create_s3_bucket("sConroy")
    urllib.request.urlretrieve('https://setuacsresources.s3-eu-west-1.amazonaws.com/image.jpeg', 'data/image.jpeg')
    s3.upload_file_to_bucket(bucketName, "data/image.jpeg", "image/jpeg")
    s3.upload_file_to_bucket(bucketName, "data/index.html", "text/html")
    s3.add_policy(bucketName)
    s3.website_configuration(bucketName, website_configuration)

def main():
    logger = log.setup_logger(name="acs_main")
    logger.info("Starting ACS Project")
    launch_ec2_instance()
    # launch_S3_bucket()
    


if __name__ == "__main__":
    main()
    