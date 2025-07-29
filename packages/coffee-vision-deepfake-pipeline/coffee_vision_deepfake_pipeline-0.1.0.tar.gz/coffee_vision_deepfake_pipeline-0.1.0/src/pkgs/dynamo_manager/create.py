import boto3

def connect_dynamo_table(aws_access_key_id, aws_secret_access_key, aws_session_token, region_name, dynamo_table_name):
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key_id ,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token ,
            region_name=region_name ,  
        )
        table = dynamodb.Table(dynamo_table_name)
        # Attempt to describe the table to confirm connection and table existence
        table.table_status  # Accessing this forces a metadata fetch
    except Exception as e:
        raise ValueError(f"Failed to connect to DynamoDB table: {str(e)}")
    
    return table

