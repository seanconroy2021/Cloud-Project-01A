import subprocess
import utils.logger as log
logger = log.setup_logger(name="command line")
def run_command(key, ipAddress, command):
    try:
        logger.info(f"Running command: {command}")
        subprocess.run(f"chmod 400 {key}", shell=True)
        ssh_command = f'ssh -i {key} ec2-user@{ipAddress} -o StrictHostKeyChecking=no {command}'
        result = subprocess.run(ssh_command, shell=True)
        logger.info(f"Command result: {result}")
        return result
    except Exception as e:
        log.error(f"Failed to run command: {e}")
        return None


def upload_file(key, ipAddress, file):
    try:
        logger.info(f"Uploading file: {file}")
        subprocess.run(f'chmod 400 {key}', shell=True)
        ssh_command = f'scp -i {key} -o StrictHostKeyChecking=no {file} ec2-user@{ipAddress}:.'
        result = subprocess.run(ssh_command, shell=True)
        return result
    except Exception as e:
        log.error(f"Failed to upload file: {e}")
        return None


