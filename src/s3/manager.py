import json

import boto3

import utils.logger as log
import utils.randomName as randomName

logger = log.setup_logger(name="s3 Manager")
s3_client = boto3.client("s3")
s3_resource = boto3.resource("s3")


def create_s3_bucket(bucketName):
    try:
        bucketName = randomName.randomName(bucketName)
        s3_client.create_bucket(Bucket=bucketName)
        logger.info(f"Created bucket: {bucketName}")
        return bucketName
    except Exception as e:
        logger.error(f"Failed to create S3 bucket: {e}")
        return None


def upload_file_to_bucket(bucketName, filePath, contentType):
    try:
        fileName = filePath.split("/")[-1]
        response = s3_resource.Object(bucketName, fileName).put(
            Body=open(
                filePath,
                "rb",
            ),
            ContentType=contentType,
        )
        logger.info(f"Uploaded file: {filePath} to bucket: {bucketName}")
        return response
    except Exception as e:
        logger.error(f"Failed to upload file: {filePath} to bucket: {bucketName}: {e}")
        return None


def add_policy(bucketName):
    try:
        s3_client.delete_public_access_block(Bucket=bucketName)
        logger.info(f"Deleted public access block: {bucketName}")
    except Exception as e:
        logger.error(f"Failed to delete public access block: {e}")
    try:
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{bucketName}/*",
                }
            ],
        }
        s3_resource.Bucket(bucketName).Policy().put(Policy=json.dumps(bucket_policy))

        logger.info(f"Added policy to bucket: {bucketName}")
    except Exception as e:
        logger.error(f"Failed to add policy to {bucketName}: {e}")
        return None


def website_configuration(bucketName, configuration):
    try:
        bucket_website = s3_resource.BucketWebsite(bucketName)
        bucket_website.put(WebsiteConfiguration=configuration)
        logger.info(f"Configured website: {bucketName}")
    except Exception as e:
        logger.error(f"Failed to configure website: {bucketName}: {e}")
        return None
