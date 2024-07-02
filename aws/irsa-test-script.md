- Can Run the below script on amazon/cli container running inside a pod configured with [IRSA](https://aws.amazon.com/blogs/opensource/introducing-fine-grained-iam-roles-service-accounts/)

```bash
yum install jq -y

aws sts get-caller-identity

# Assume role and capture the output
TEMP_CREDS=$(aws sts assume-role --role-arn arn:aws:iam::915632791698:role/suran-s3-role --role-session-name alter-ego)

env | grep -e AWS_ -e WEB -e ROLE

# Extract and export credentials using jq
export AWS_ACCESS_KEY_ID=$(echo $TEMP_CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $TEMP_CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $TEMP_CREDS | jq -r '.Credentials.SessionToken')

# Verify that credentials are set
echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY"
echo "AWS_SESSION_TOKEN: $AWS_SESSION_TOKEN"

# Create sample file to upload
echo "Harness Automates" > sample-file.txt

# Copy the file to S3 with region
aws s3 cp sample-file.txt s3://suranbucketcs1/alter-ego/sample-file.txt --region us-east-1

mkdir justansible

aws s3 cp s3://suranbucketcs1/alter-ego/sample-file.txt ./justansible --region us-east-1
```
