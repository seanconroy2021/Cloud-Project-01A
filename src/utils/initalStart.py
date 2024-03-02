import json
import os

import commandLine.manager as cmd
import security.manager as security
import utils.logger as log
import utils.randomName as randomName

logger = log.setup_logger(name="Initial Setup (only run once)")
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
outbound = [
    {
        "IpProtocol": "-1",
        "FromPort": -1,
        "ToPort": -1,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
    }
]


def setup_security_group():
    try:
        name = randomName.randomName("SconroySecurityGroup")
        id = security.create_security_group(
            group_name=name,
            description="Sconroy Security Group",
            inboundRules=inbound,
            outboundRules=outbound,
        )
        logger.info(f"Security group created id: {id} name: {name}")
        return id
    except Exception as e:
        logger.error(f"Failed to setup security group : {e}")


def setup_key_pair():
    try:
        name = randomName.randomName("sconroyKey")
        keyName = security.create_key_pair(name)
        logger.info(f"Key pair created in data/{keyName}.pem")
        return keyName
    except Exception as e:
        logger.error(f"Failed to setup key pair: {e}")


def check_aws_working():
    response = cmd.run_local_command("aws iam list-users")
    if response.returncode == 0:
        logger.info("AWS is working")
    else:
        logger.error("AWS is not working")
        logger.info("Please make sure you have AWS (BOTO3) installed and configured.")
        exit(1)


def setup():
    check_aws_working()
    configFile = "data/setupConfig.json"
    if os.path.exists(configFile):
        logger.info("Configuration file exists, loading configuration...")
        with open(configFile, "r") as file:
            config = json.load(file)
            securityId = config.get("securityId")
            keyName = config.get("keyName")
            logger.info("Configuration loaded successfully.")
            return securityId, keyName
    else:
        logger.info("Configuration file not found, proceeding with setup...")
        securityId = setup_security_group()
        keyName = setup_key_pair()
        config = {"securityId": securityId, "keyName": keyName}
        with open(configFile, "w") as file:
            json.dump(config, file, indent=4)
        logger.info("Setup complete.")
        return securityId, keyName
