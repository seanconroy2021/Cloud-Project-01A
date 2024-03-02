import json
import security.manager as security
import utils.logger as log
import os
logger = log.setup_logger(name="Initial Setup (only run once)")
inbound=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 27017,
            'ToPort': 27017,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
outbound=[
        {
            'IpProtocol': '-1',
            'FromPort': -1,
            'ToPort': -1,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]

def setup_security_group():
    try :
        id = security.create_security_group(
            group_name="SConroyGroup12",
            description="ACS Security Group",
            inboundRules=inbound,
            outboundRules=outbound
        )
        logger.info(f"Security group created id: {id}")
        return id
    except Exception as e:
        logger.error(f"Failed to setup security group : {e}")

def setup_key_pair():
    try:
        config_file = "setupConfig.json"
        keyName = security.create_key_pair("SConroyKey")
        logger.info(f"Key pair created in data/{keyName}.pem")
        return keyName
    except Exception as e:
        logger.error(f"Failed to setup key pair: {e}")

def setup():
    config_file = "data/setupConfig.json"
    if os.path.exists(config_file):
        logger.info("Configuration file exists, loading configuration...")
        with open(config_file, 'r') as file:
            config = json.load(file)
            securityId = config.get('securityId')
            keyName = config.get('keyName')
            logger.info("Configuration loaded successfully.")
            return securityId, keyName
    else:
        logger.info("Configuration file not found, proceeding with setup...")
        securityId = setup_security_group()
        keyName = setup_key_pair()
        config = {
            'securityId': securityId,
            'keyName': keyName
        }
        with open(config_file, 'w') as file:
            json.dump(config, file, indent=4)
        logger.info("Setup complete.")
        return securityId, keyName
    
   