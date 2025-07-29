import boto3
from botocore.exceptions import ClientError

def createS3Client(aws_access_key_id, aws_secret_access_key, aws_session_token):
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )

def check_s3_connection(s3_client):
    try:
        s3_client.list_buckets()
        print("S3 connection successful.")
        return True
    except ClientError as e:
        print(f"Failed to connect to S3: {e}")
        return False
    