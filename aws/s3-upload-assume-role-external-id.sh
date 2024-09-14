cat << EOF> OP.txt
I love Ansible Automation!
EOF

ROLE_ARN='arn:aws:iam::AWS_ACCOUNT_ID:role/ROLE_ID'
EXTERNAL_ID='12345'
DURATION='3600'
BUCKET_NAME='s3-bucket'
AWS_REGION='us-east-2'
FILE_NAME=OP.txt

# Assume role with web identity and capture the output
ASSUME_ROLE_OUTPUT=$(aws sts assume-role \
  --duration-seconds $DURATION \
  --role-session-name "app1" \
  --role-arn $ROLE_ARN \
  --external-id $EXTERNAL_ID)

# Extract and export credentials
export AWS_ACCESS_KEY_ID=$(echo "$ASSUME_ROLE_OUTPUT" | grep -o '"AccessKeyId": "[^"]*' | sed 's/"AccessKeyId": "//')
export AWS_SECRET_ACCESS_KEY=$(echo "$ASSUME_ROLE_OUTPUT" | grep -o '"SecretAccessKey": "[^"]*' | sed 's/"SecretAccessKey": "//')
export AWS_SESSION_TOKEN=$(echo "$ASSUME_ROLE_OUTPUT" | grep -o '"SessionToken": "[^"]*' | sed 's/"SessionToken": "//')

# List all S3 buckets
echo "Listing S3 buckets:"
aws s3 ls

# Upload $FILE_NAME to the specified S3 bucket
echo "Uploading test1.txt to s3://$BUCKET_NAME/ in region $AWS_REGION"
aws s3 cp $FILE_NAME s3://$BUCKET_NAME/ --region $AWS_REGION

# Check if the upload was successful
if [ $? -eq 0 ]; then
    echo "File uploaded successfully."
else
    echo "Error: Failed to upload file."
    exit 1
fi
