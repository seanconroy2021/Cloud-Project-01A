import time
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
            UserData=userData,
        )
        logger.info(f"Launched EC2 Instance: {instance[0].id}")
        waiter_status([instance[0].id], "running")
        ip = get_public_ip(instance[0].id)
        dns = get_public_dns(instance[0].id)
        return ip, dns
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

def get_public_dns(id):
    try:
        instance = ec2_resource.Instance(id)
        logger.info(f"Public DNS: {instance.public_dns_name}")
        return instance.public_dns_name
    except Exception as e:
        logger.error(f"Failed to get public DNS: {e}")
        return None

def waiter_status(id, state):
    try:
        waiter = ec2_client.get_waiter(f"instance_{state}")
        logger.info(f"Waiting for instance {id} to be {state}...")
        waiter.wait(InstanceIds=id, WaiterConfig={"Delay": 20, "MaxAttempts": 20})
        logger.info(f"Instance {state} successfully.")
    except Exception as e:
        logger.error(f"Error waiting for instance to {state}: {e}")
