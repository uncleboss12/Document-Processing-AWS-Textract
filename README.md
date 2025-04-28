
# AWS Lambda Textract Integration with S3 and API Gateway

This project demonstrates how to create an AWS Lambda function that integrates with Amazon S3 and Amazon Textract to extract text from PDF and image files. The extracted text is saved back to an S3 bucket. Optionally, an API Gateway can be used to upload files to the S3 bucket.

---

## **Architecture Overview**

1. **S3 Bucket**: Stores the uploaded documents (PDFs or images).
2. **Lambda Function**: Triggered by S3 events to process the uploaded files using Amazon Textract.
3. **Amazon Textract**: Extracts text from the uploaded documents.
4. **Processed Folder**: The extracted text is saved in a `processed/` folder in the same S3 bucket.
5. **Optional API Gateway**: Provides an HTTP endpoint to upload files to the S3 bucket.

---

## **Features**

- Extracts text from supported document formats (PDF, JPEG, PNG, TIFF).
- Handles both synchronous and asynchronous Textract operations.
- Saves extracted text to a `processed/` folder in the S3 bucket.
- Optional API Gateway integration for file uploads.

---

## **Setup Instructions**

### **1. Prerequisites**
- An AWS account.
- AWS CLI installed and configured.
- Basic knowledge of AWS services (S3, Lambda, Textract, API Gateway).

---

### **2. Create an S3 Bucket**
1. Go to the **S3 Console** and create a bucket (e.g., `document-processing-bucket`).
2. Enable **event notifications** for the bucket:
   - Go to the **Properties** tab.
   - Under **Event notifications**, create a new notification.
   - Set the event type to `PUT` and configure it to trigger the Lambda function (created in Step 4).

---

### **3. Create an IAM Role for Lambda**
1. Go to the **IAM Console** and create a new role.
2. Attach the following policies:
   - **AmazonS3FullAccess** (or restrict it to specific buckets).
   - **AmazonTextractFullAccess**.
   - **AWSLambdaBasicExecutionRole**.
3. Note the **Role ARN** for use in the Lambda function.

---

### **4. Create the Lambda Function**
1. Go to the **Lambda Console** and create a new function.
2. Choose **Author from scratch** and provide:
   - Function name: `process-document-lambda`.
   - Runtime: Python 3.9 (or any supported runtime).
   - Execution role: Use the IAM role created in Step 3.
3. Add the following code to the Lambda function:

```python
import boto3
import json
import os
import time

# Initialize AWS clients
s3 = boto3.client('s3')
textract = boto3.client('textract')

def lambda_handler(event, context):
    # Get the bucket name and file key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    print(f"Processing file: {file_key} from bucket: {bucket_name}")

    try:
        # Start asynchronous Textract operation for PDFs
        response = textract.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': file_key}}
        )
        job_id = response['JobId']
        print(f"Textract job started with JobId: {job_id}")

        # Wait for the Textract job to complete
        status = "IN_PROGRESS"
        while status == "IN_PROGRESS":
            time.sleep(5)  # Wait for 5 seconds before checking the status
            job_status = textract.get_document_text_detection(JobId=job_id)
            status = job_status['JobStatus']
            print(f"Job status: {status}")

        if status == "SUCCEEDED":
            # Extract text from the Textract response
            extracted_text = ""
            for block in job_status['Blocks']:
                if block['BlockType'] == 'LINE':
                    extracted_text += block['Text'] + "\n"

            # Save the extracted text to a new file in the "processed/" folder
            output_key = f"processed/{os.path.basename(file_key)}.txt"
            s3.put_object(
                Bucket=bucket_name,
                Key=output_key,
                Body=extracted_text
            )
            print(f"Text extracted and saved to {output_key}")
        else:
            print(f"Textract job failed with status: {status}")
            raise Exception(f"Textract job failed with status: {status}")

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f"Text extracted and saved to {output_key}")
    }
