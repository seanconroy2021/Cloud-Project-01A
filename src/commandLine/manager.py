import subprocess
import utils.logger as log
logger = log.setup_logger(name="command line")
def run_command(key, ipAddress, command):
    try:
        logger.info(f"Running command: {command}")
        subprocess.run(f"chmod 400 {key}", shell=True)
        ssh_command = f'ssh -i {key} ec2-user@{ipAddress} -o StrictHostKeyChecking=no "{command}"'
        result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output_handler(result)
        return result
    except Exception as e:
        log.error(f"Failed to run command: {e}")
        return None

def run_local_command(command):
    try:
        logger.info(f"Running local command: {command}")
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output_handler(result)
        return result
    except Exception as e:
        log.error(f"Failed to run local command: {e}")
        return None

def upload_file(key, ipAddress, file):
    try:
        logger.info(f"Uploading file: {file}")
        subprocess.run(f'chmod 400 {key}', shell=True)
        ssh_command = f'scp -i {key} -o StrictHostKeyChecking=no {file} ec2-user@{ipAddress}:~'
        print(ssh_command)
        result = subprocess.run(ssh_command, shell=True, text=True)
        return result
    except Exception as e:
        log.error(f"Failed to upload file: {e}")
        return None

def output_handler(result):
    output = result.stdout
    logger.info(f"Command output: {output}")


