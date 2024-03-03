import json
import os

import commandLine.manager as cmd
import security.manager as security
import utils.logger as log
import utils.randomName as randomName

logger = log.setup_logger(name="Initial Setup before launch")
inbound = [
    {
        "IpProtocol": "tcp",
        "FromPort": 80,
        "ToPort": 80,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
    },
    {
        "IpProtocol": "tcp",
        "FromPort": 22,
        "ToPort": 22,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
    },
    {
        "IpProtocol": "tcp",
        "FromPort": 27017,
        "ToPort": 27017,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
    },
]

# These functions are used to setup the security group and key pair for the EC2 instance before launching the EC2 instance and S3 bucket.
# These functions use helper functions created in the security.manager.py & randomName.py files.
def setup_security_group():
    """
    This function creates a security group for the EC2 instance.
    name is random with the prefix "SconroySecurityGroup"
    """
    try:
        name = randomName.randomName("SconroySecurityGroup")
        print(name)
        id = security.create_security_group(
            groupName=name,
            description="Sconroy Security Group",
            inboundRules=inbound,
            outboundRules=[],
        )
        logger.info(f"Security group created id: {id} name: {name}")
        return id
    except Exception as e:
        logger.error(f"Failed to setup security group : {e}")
        raise e


def setup_key_pair():
    """
    This function creates a key pair for the EC2 instance.
    name is random with the prefix "sconroyKey"
    """
    try:
        name = randomName.randomName("sconroyKey")
        keyName = security.create_key_pair(name)
        logger.info(f"Key pair created in data/{keyName}.pem")
        return keyName
    except Exception as e:
        logger.error(f"Failed to setup key pair: {e}")
        raise e


def check_aws_working():
    """
    This function checks if AWS is working it run the command "aws iam list-users" locally and checks the return code.
    If the return code is 0 then AWS is working else it is not working.
    It will also log the error/output of the command.
    If response anything else then 0 it will exit the program.
    """
    response = cmd.run_local_command("aws iam list-users") # run the command "aws iam list-users" locally it check to see if aws has the right credentials.
    if response.returncode == 0:
        logger.info("AWS is working")
    else:
        logger.error("AWS is not working")
        logger.info("Please make sure you have AWS (BOTO3) installed and configured.")
        exit(1)


def setup():
    check_aws_working()
    configFile = "data/setupConfig.json"
    # Check if the configuration file exists if their is a configuration file in /data/setupConfig.json
    # the function will then load it in and return the securityId and keyName
    if os.path.exists(configFile):
        logger.info("Configuration file exists, loading configuration...")
        with open(configFile, "r") as file:
            config = json.load(file)
            securityId = config.get("securityId")
            keyName = config.get("keyName")
            logger.info("Configuration loaded successfully.")
            return securityId, keyName
    else:
        # If their is no configuration file in /data/setupConfig.json
        # the function will then create a security group and key pair and save the id and key name in the configuration file.
        # It will then return the securityId and keyName
        logger.info("Configuration file not found, proceeding with setup...")
        securityId = setup_security_group()
        keyName = setup_key_pair()
        config = {"securityId": securityId, "keyName": keyName}
        with open(configFile, "w") as file:
            json.dump(config, file, indent=4)
        logger.info("Setup complete.")
        return securityId, keyName
