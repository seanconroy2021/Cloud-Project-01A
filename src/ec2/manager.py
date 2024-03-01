import boto3

import utils.logger as log

logger = log.setup_logger(name="ec2_manager")

ec2_resource = boto3.resource("ec2")
ec2_client = boto3.client("ec2")


def launch_ec2_instance(instanceName, keyName, secuirtyGroupId,  userData):
    try:
        instance = ec2_resource.create_instances(
            ImageId=get_amazon_linux_ami(),
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName=keyName,
            SecurityGroupIds=[secuirtyGroupId],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": f"{instanceName}"}],
                }
            ],
            UserData='''#!/bin/bash
yum update -y && yum install -y httpd && systemctl start httpd && systemctl enable httpd && echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html'''
        

        )
        print(userData)
        print('aksakskaksaksaksakskasks')
        logger.info(f"Launched EC2 Instance: {instance[0].id}")
        waiter([instance[0].id], "running")
        return [instance[0]]
    except Exception as e:
        logger.error(f"Failed to launch EC2 instance: {e}")


def get_amazon_linux_ami():
    try:
        logger.info("Getting Amazon Linux AMI...")
        return "ami-0440d3b780d96b29d"
    except Exception as e:
        logger.error(f"Failed to get Amazon Linux AMI: {e}")
        return None


def get_public_ip(id):
    try:
        instance = ec2_resource.Instance(id)
        logger.info(f"Public IP: {instance.public_ip_address}")
        return instance.public_ip_address
    except Exception as e:
        logger.error(f"Failed to get public IP: {e}")
        return None


def waiter(id, state):
    try:
        waiter = ec2_client.get_waiter(f"instance_{state}")
        logger.info(f"Waiting for instance {id} to be {state}...")
        waiter.wait(InstanceIds=id)
        logger.info(f"Instance {state} successfully.")
    except Exception as e:
        logger.error(f"Error waiting for instance to {state}: {e}")
