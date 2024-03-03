import boto3

from utils.logger import setup_logger

logger = setup_logger(name="Security_manager")

ec2_client = boto3.client("ec2")


def create_security_group(groupName, description, inboundRules, outboundRules):
    """
    This function is a helper function used to create a security group for an EC2 instance.
    It takes in the group name, description, inbound rules and outbound rules. e.g. of inbound/outbound rules:
    [    {
        "IpProtocol": "tcp",
        "FromPort": 27017,
        "ToPort": 27017,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        },
    ]
    """
    try:
        # link:https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/create_security_group.html#create-security-group
        response = ec2_client.create_security_group(
            Description=description,
            GroupName=groupName,
            TagSpecifications=[
                {
                    "ResourceType": "security-group",
                    "Tags": [
                        {"Key": "Name", "Value": groupName},
                    ],
                },
            ],
        )
        group_id = response["GroupId"]
        add_rules(group_id, inboundRules, outboundRules)
        logger.info(f"Created security group: {group_id}")
        return group_id
    except Exception as e:
        logger.error(f"Failed to create security group: {e}")
        raise e


def add_rules(GroupId, Inbound, Outbound):
    """
    This function is a helper function for the security group to add inbound and outbound rules.
    It takes in the group id, inbound rules and outbound rules.
    """
    try:
        # link Inboud (ingress) https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/authorize_security_group_ingress.html#authorize-security-group-ingress
        if Inbound is None or Inbound is []:
            logger.info(f"No inbound rules to add to security group: {GroupId}")
            dataInbound = None
        else:
            logger.info(f"Adding inbound rules to security group: {GroupId}")
            dataInbound = ec2_client.authorize_security_group_ingress(
                GroupId=GroupId, IpPermissions=Inbound
            )

        # link Outbound (egress) https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/authorize_security_group_egress.html#authorize-security-group-egress
        if Outbound is None or Outbound is []:
            logger.info(f"No outbound rules to add to security group: {GroupId}")
            dataOutbound = None
        else:
            logger.info(f"Adding outbound rules to security group: {GroupId}")
            dataOutbound = ec2_client.authorize_security_group_egress(
                GroupId=GroupId, IpPermissions=Outbound
            )
        logger.info(f"Added rules to security group: {GroupId}")
    except Exception as e:
        logger.error(f"Failed to add rules to security group: {e}")
    return dataInbound, dataOutbound


def create_key_pair(KeyName):
    """
    This function is a helper function used to create a key pair for an EC2 instance.
    It takes in the key name and creates the key pair (take the data of the key and write it to a file at
    /data/key.pem).
    It will also return the key name once created.
    """
    try:
        # link:https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/create_key_pair.html#create-key-pair
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
        write_to_key_to_file(response, f"data/{KeyName}.pem")
        logger.info(f"Created key pair: {KeyName}")
        return KeyName
    except Exception as e:
        logger.error(f"Failed to create key pair: {e}")
        raise e


def write_to_key_to_file(response, filename):
    """
    This function is a helper function to write the key to a file.
    It takes in the response and get the key material and writes it to a file.
    """
    try:
        with open(filename, "w") as file:
            file.write(response["KeyMaterial"])
        logger.info(f"Key written to file: data/{filename}.pem")
    except Exception as e:
        logger.error(f"Failed to write key to file: {e}")
