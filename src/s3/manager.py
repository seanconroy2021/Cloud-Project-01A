import json

import boto3

import utils.logger as log
import utils.randomName as randomName

logger = log.setup_logger(name="s3 Manager")
s3_client = boto3.client("s3")
s3_resource = boto3.resource("s3")


def get_region():
    """
    This function is a helper function to get the region of the AWS account.
    It returns the region of the AWS based on your config file.
    """
    try:
        # link https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html
        # Since not seeting any session it will use the default profile and region information from your ./aws/config.
        # This then allow us to get the region of the account.
        session = boto3.session.Session()
        currentRegion = session.region_name
        logger.info(f"Region: {currentRegion}")
        return currentRegion
    except Exception as e:
        logger.error(f"Failed to get region: {e}")
        raise e


def create_s3_bucket(bucketName):
    """
    This is a helper function to create an S3 bucket.
    It takes in the bucket name and creates the bucket.
    Returns the bucket name (that is now random-name ).
    """
    try:
        bucketName = randomName.randomName(bucketName)
        region = get_region()
        s3_client.create_bucket(Bucket=bucketName)
        logger.info(f"Created bucket: {bucketName}")
        return bucketName, region
    except Exception as e:
        logger.error(f"Failed to create S3 bucket: {e}")
        raise e


# Had add content type to be able to reach the index.html file
def upload_file_to_bucket(bucketName, filePath, contentType):
    """
    This function is a helper function used to upload a file to an S3 bucket.
    It takes in the bucket name, file path and content type e.g. "text/html".
    """
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
        raise e


def add_policy(bucketName):
    """
    This function is a helper function used to add a generic policy to an S3 bucket.
    It takes in the bucket name and adds a policy to the bucket.
    (This policy allows public read access to the bucket and delete the public block.)
    """
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
        raise e


def website_configuration(bucketName, configuration):
    """
    This function is a helper function used to configure a website on an S3 bucket.
    It takes in the bucket name and then sets up the S3 bucket to be a website.
    Also, it takes in the configuration for the website. e.g.
    {
    "IndexDocument": {"Suffix": "index.html"},
    }
    """
    try:
        bucket_website = s3_resource.BucketWebsite(bucketName)
        bucket_website.put(WebsiteConfiguration=configuration)
        logger.info(f"Configured website: {bucketName}")
    except Exception as e:
        logger.error(f"Failed to configure website: {bucketName}: {e}")
        raise e
