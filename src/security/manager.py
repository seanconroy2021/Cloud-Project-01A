import boto3

from utils.logger import setup_logger

logger = setup_logger(name="Security_manager")

ec2_client = boto3.client("ec2")


def create_security_group(group_name, description, inboundRules, outboundRules):
    try:
        response = ec2_client.create_security_group(
            Description=description,
            GroupName=group_name,
            TagSpecifications=[
                {
                    "ResourceType": "security-group",
                    "Tags": [
                        {"Key": "Name", "Value": group_name},
                    ],
                },
            ],
        )
        group_id = response["GroupId"]
        add_rules(group_id, inboundRules)
        add_rules(group_id, outboundRules)
        logger.info(f"Created security group: {group_id}")
        return group_id
    except Exception as e:
        logger.error(f"Failed to create security group: {e}")
        return None


def add_rules(GroupId, ipPermissions):
    try:
        data = ec2_client.authorize_security_group_ingress(
            GroupId=GroupId, IpPermissions=ipPermissions
        )
        logger.info(f"Added rules to security group: {GroupId}")
    except Exception as e:
        logger.error(f"Failed to add rules to security group: {e}")
    return data


def create_key_pair(KeyName):
    try:
        response = ec2_client.create_key_pair(
            KeyName=KeyName,
            KeyType="rsa",
            TagSpecifications=[
                {
                    "ResourceType": "key-pair",
                    "Tags": [
                        {"Key": "Name", "Value": f"{KeyName}"},
                    ],
                },
            ],
            KeyFormat="pem",
        )
        write_to_file(response, f"data/{KeyName}.pem")
        logger.info(f"Created key pair: {KeyName}")
        return KeyName
    except Exception as e:
        logger.error(f"Failed to create key pair: {e}")
        return None


def write_to_file(response, filename):
    with open(filename, "w") as file:
        file.write(response["KeyMaterial"])
