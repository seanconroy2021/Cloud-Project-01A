import boto3

import utils.logger as log

logger = log.setup_logger(name="ec2 Manager")

# link:https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#ec2
# link:https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrationec2.html
# These are the boto3 resources and clients that we will use to interact with AWS.
ec2_resource = boto3.resource("ec2")
ec2_client = boto3.client("ec2")

# This is a helper function to launch an EC2 instance.
# It takes in the instance name, key name, security group id and user data.
# It then creates an EC2 instance and returns the public IP and DNS.


def launch_ec2_instance(instanceName, keyName, secuirtyGroupId, userData):
    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/service-resource/create_instances.html#create-instances
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
        raise e


# Link:https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_images.html#describe-images
# This is a helper function to get the lastest Amazon Linux AMI for the EC2 helper functions.
# this was very hard to setup I ended up using "aws ec2 describe-images" and then searched the json for AMI ID e.g.ami-0440d3b780d96b29d"
# and then used the json to create the filter below here is the json I used to create the filter below.
# #{
#             "Architecture": "x86_64",
#             "CreationDate": "2024-02-16T21:29:42.000Z",
#             "ImageId": "ami-0440d3b780d96b29d",
#             "ImageLocation": "amazon/al2023-ami-2023.3.20240219.0-kernel-6.1-x86_64",
#             "ImageType": "machine",
#             "Public": true,
#             "OwnerId": "137112412989",
#             "PlatformDetails": "Linux/UNIX",
#             "UsageOperation": "RunInstances",
#             "State": "available",
#             "BlockDeviceMappings": [
#                 {
#                     "DeviceName": "/dev/xvda",
#                     "Ebs": {
#                         "DeleteOnTermination": true,
#                         "Iops": 3000,
#                         "SnapshotId": "snap-0fc9d6b92707fe1b2",
#                         "VolumeSize": 8,
#                         "VolumeType": "gp3",
#                         "Throughput": 125,
#                         "Encrypted": false
#                     }
#                 }
#             ],
#             "Description": "Amazon Linux 2023 AMI 2023.3.20240219.0 x86_64 HVM kernel-6.1",
#             "EnaSupport": true,
#             "Hypervisor": "xen",
#             "ImageOwnerAlias": "amazon",
#             "Name": "al2023-ami-2023.3.20240219.0-kernel-6.1-x86_64",
#             "RootDeviceName": "/dev/xvda",
#             "RootDeviceType": "ebs",
#             "SriovNetSupport": "simple",
#             "VirtualizationType": "hvm",
#             "BootMode": "uefi-preferred",
#             "DeprecationTime": "2024-05-16T21:30:00.000Z",
#             "ImdsSupport": "v2.0"
#         },
def get_amazon_linux_ami():
    """
    This is a helper function to get the latest Amazon Linux AMI it will return the AMI ID.
    """
    try:
        logger.info("Getting Amazon Linux AMI...")
        response = ec2_client.describe_images(
            Owners=["amazon"],
            Filters=[
                {"Name": "name", "Values": ["al2023-ami-2023.*.*-kernel-6.1-x86_64"]},
                {"Name": "architecture", "Values": ["x86_64"]},
                {"Name": "image-type", "Values": ["machine"]},
                {"Name": "state", "Values": ["available"]},
                {"Name": "root-device-type", "Values": ["ebs"]},
                {"Name": "virtualization-type", "Values": ["hvm"]},
                {"Name": "hypervisor", "Values": ["xen"]},
                {"Name": "ena-support", "Values": ["true"]},
                {"Name": "sriov-net-support", "Values": ["simple"]},
                {"Name": "boot-mode", "Values": ["uefi-preferred"]},
            ],
        )
        # Sort the images by the creation date and get the most recent one had to use Github Copilot to get this fully work.
        amis = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
        if amis:
            latestAmi = amis[0]  # The most recent AMI
            logger.info(f"Specific Amazon Linux AMI ID found: {latestAmi['ImageId']}")
            return latestAmi["ImageId"]
        else:
            logger.error("No Amazon Linux AMI found.")
            raise Exception("No specific Amazon Linux AMI found.")
    except Exception as e:
        logger.error(f"Failed to get Amazon Linux AMI: {e}")
        raise e


# This is a helper function to get the public IP of an EC2 instance.
# It takes in the instance id and returns the public IP.
def get_public_ip(id):
    try:
        instance = ec2_resource.Instance(id)
        logger.info(f"Public IP: {instance.public_ip_address}")
        return instance.public_ip_address
    except Exception as e:
        logger.error(f"Failed to get public IP: {e}")
        raise e


# This is a helper function simlar to above instead get the public DNS of an EC2 instance.
# It takes in the instance id and returns the public DNS.
def get_public_dns(id):
    try:
        instance = ec2_resource.Instance(id)
        logger.info(f"Public DNS: {instance.public_dns_name}")
        return instance.public_dns_name
    except Exception as e:
        logger.error(f"Failed to get public DNS: {e}")
        raise e


# This is a helper function that is used by the EC2 helper functions to wait for an instance to reach a certain state.
# It takes in the instance id and the state to wait for.
def waiter_status(id, state):
    try:
        waiter = ec2_client.get_waiter(f"instance_{state}")
        logger.info(f"Waiting for instance to be {state}...")
        waiter.wait(InstanceIds=id, WaiterConfig={"Delay": 20, "MaxAttempts": 20})
        logger.info(f"Instance {state} successfully.")
    except Exception as e:
        logger.error(f"Error waiting for instance to {state}: {e}")
        raise e
