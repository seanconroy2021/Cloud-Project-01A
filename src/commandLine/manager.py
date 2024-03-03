import subprocess

import utils.logger as log

logger = log.setup_logger(name="command line")

# Link:https://docs.python.org/3/library/subprocess.html#using-the-subprocess-module
# This is a helper function to run a command on a EC2 instance.
# It takes in the key path, ip address and the command to run.
def run_command(key, ipAddress, command):
    try:
        logger.info(f"Running command: {command}")
        subprocess.run(f"chmod 400 {key}", shell=True)
        ssh_command = (
            f'ssh -i {key} ec2-user@{ipAddress} -o StrictHostKeyChecking=no "{command}"'
        )
        result = subprocess.run(
            ssh_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output_handler(result)
        return result
    except Exception as e:
        log.error(f"Failed to run command: {e}")
        return None

# This is a helper function to run a command on the local machine.
# It takes in the command to run and then run it on my local machine.
def run_local_command(command):
    try:
        logger.info(f"Running local command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output_handler(result)
        return result
    except Exception as e:
        log.error(f"Failed to run local command: {e}")
        return None
    
# This is a helper function to upload a file to an EC2 instance.
# It takes in the key path, ip address and the file to upload.
def upload_file(key, ipAddress, file):
    try:
        logger.info(f"Uploading file: {file}")
        subprocess.run(f"chmod 400 {key}", shell=True)
        ssh_command = (
            f"scp -i {key} -o StrictHostKeyChecking=no {file} ec2-user@{ipAddress}:~"
        )
        print(ssh_command)
        result = subprocess.run(ssh_command, shell=True, text=True)
        return result
    except Exception as e:
        log.error(f"Failed to upload file: {e}")
        return None

# This is a helper function for the output of the command helper functions.
# It takes in the result of the command and logs the output of the command
def output_handler(result):
    output = result.stdout
    logger.info(f"Command output: {output}")