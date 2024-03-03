# Sean AWS Automation

This project is a Python-based automation tool for AWS. It is designed to help developers and automate the process of creating and managing AWS resources. What this program does: 

- Create a key pair and save it to a data/*.pem file.
- Create a new security group and add rules that allow SSH, HTTP, and 27017 (Mongo).
- Create a new EC2 instance and use userData to install and configure the HTTP server. It then created an index.html with metadata of the instance.
- Create another EC2 instance and use UserData to install and configure the MongoDB server. It then SCP and SSH into the EC2 to upload datbase.json and then run the mongo import command to import Ireland Counties.
- Create a new S3 bucket and configure the bucket to be a static website. It then uploads the index.html file to the bucket.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine:
1. Clone the repository
2. Install the required packages from requirements.txt
3. Make sure Boto3 is installed
Set up your AWS credentials. You can use the helper script 'update_aws_credentials.sh' to set up your credentials.
5. Run the src/acs_1.py file to start the automation process.

