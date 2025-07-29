import boto3
from urllib.parse import urlparse

def is_s3_folder_empty(client, s3_folder_uri: str) -> bool:
    """
    Check if an S3 folder (prefix) is empty, ignoring the folder object itself.
    
    Args:
        client: boto3 S3 client
        s3_folder_uri: S3 URI (e.g., s3://bucket-name/path/to/folder/)
    
    Returns:
        bool: True if the folder is empty (no files, only possibly the folder object itself), False otherwise
    """
    parsed = urlparse(s3_folder_uri)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/').rstrip('/') + '/'  # Ensure prefix ends with '/'

    # Handle pagination
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    for page in page_iterator:
        if 'Contents' not in page:
            return True  # No objects at all, folder is empty
        for obj in page['Contents']:
            # Ignore the folder object itself (e.g., prefix 'myfolder/' should not count)
            if obj['Key'] != prefix:
                return False  # Found an actual file or sub-object
    return True  # No objects other than possibly the folder itself