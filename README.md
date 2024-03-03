# Sean AWS Automation

This project is a Python-based automation tool for AWS. It is designed to help developers and system administrators to automate the process of creating and managing AWS resources.

This project will create and manage the following AWS resources:
create two instances of EC2:
    - One that is a MongoDB server with a public DNS and a security group that allows traffic on port 27017 and SSH on port 22

    - One that is a web server with a public IP and a security group that allows traffic on port 80 and SSh on port 22
  
create an S3 bucket:
    - The bucket is public and made into a lsstatic website which will display an image of SETU it will also display the S3 bucket name and the URl of the S3 bucket.


## Getting Started

Instructions on setting up your project locally.
For example, if your project requires Python, you might need to instruct users to create a virtual environment and install dependencies.

### Prerequisites

What things you need to install the software and how to install them.

### Installing

A step by step series of examples that tell you how to get a development environment running.

## Running the scripts

Explain how to run the automated scripts.

- `src/acs_1.py`: Description of what this script does.
- `src/ec2/manager.py`: Description of what this script does.
- `src/s3/manager.py`: Description of what this script does.
- `src/security/manager.py`: Description of what this script does.
- `src/commandLine/manager.py`: Description of what this script does.
- `src/utils/initalStart.py`: Description of what this script does.
- `src/utils/logger.py`: Description of what this script does.
- `src/utils/openBrowser.py`: Description of what this script does.
- `src/utils/randomName.py`: Description of what this script does.

## Built With

Mention the tech stack you used for this project.

## Authors

Your Name

## License

Add link to license file

## Acknowledgments

Hat tip to anyone whose code was used
Inspiration