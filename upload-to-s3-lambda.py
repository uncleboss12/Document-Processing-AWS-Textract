import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Extract the file content and filename from the API Gateway event
        body = event['body']
        decoded_body = base64.b64decode(body)  # Decode the base64-encoded file content
        bucket_name = "buckey-upload-api"  # Replace with your S3 bucket name
        file_name = event['headers']['filename']  # Filename passed in the headers

        # Upload the file to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=decoded_body
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f"File {file_name} uploaded successfully to {bucket_name}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
