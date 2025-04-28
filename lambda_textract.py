import boto3
import json
import os

# Initialize AWS clients
s3 = boto3.client('s3')
textract = boto3.client('textract')

def lambda_handler(event, context):
    # Get the bucket name and file key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    # Call Textract to extract text from the document
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': file_key}}
    )
    
    # Extract text from the Textract response
    extracted_text = ""
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            extracted_text += item['Text'] + "\n"
    
    # Save the extracted text to a new file in the "processed/" folder
    output_key = f"processed/{os.path.basename(file_key)}.txt"
    s3.put_object(
        Bucket=bucket_name,
        Key=output_key,
        Body=extracted_text
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(f"Text extracted and saved to {output_key}")
    }
