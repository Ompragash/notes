export HARNESS_API_PAT="REPLACE"
export HARNESS_ACCOUNT_ID="REPLACE"
export ASSUME_ROLE_ARN="arn:aws:iam::58905456789:role/aws_role"
export AWS_REGION="us-west-2"
export AWS_BUCKET="SAMPLE_BUCKET"

# Extract OIDC ID Token from Harness 
export PLUGIN_OIDC_ID_TOKEN=$(curl --location "https://app.harness.io/gateway/ng/api/oidc/id-token/aws" \
  --header "Content-Type: application/json" \
  --header "x-api-key: $HARNESS_API_PAT" \
  --data "{
    \"oidcIdTokenCustomAttributesStructure\": {
      \"account_id\": \"$HARNESS_ACCOUNT_ID\"
    }
  }" | grep -o '"data":"[^"]*' | sed 's/"data":"//')

# Assume role with web identity and capture the output
ASSUME_ROLE_OUTPUT=$(aws sts assume-role-with-web-identity \
  --duration-seconds 3600 \
  --role-session-name "app1" \
  --role-arn "$ASSUME_ROLE_ARN" \
  --web-identity-token $PLUGIN_OIDC_ID_TOKEN)

# Extract and export credentials
export AWS_ACCESS_KEY_ID=$(echo "$ASSUME_ROLE_OUTPUT" | grep -o '"AccessKeyId": "[^"]*' | sed 's/"AccessKeyId": "//')
export AWS_SECRET_ACCESS_KEY=$(echo "$ASSUME_ROLE_OUTPUT" | grep -o '"SecretAccessKey": "[^"]*' | sed 's/"SecretAccessKey": "//')
export AWS_SESSION_TOKEN=$(echo "$ASSUME_ROLE_OUTPUT" | grep -o '"SessionToken": "[^"]*' | sed 's/"SessionToken": "//')

# Verify
echo "Access Key: $AWS_ACCESS_KEY_ID"
echo "Secret Key: $AWS_SECRET_ACCESS_KEY"
echo "Session Token: $AWS_SESSION_TOKEN"

# Create sample file to upload
echo "Harness Automates" > sample-file.txt

# Copy the file to S3 with region
aws s3 cp sample-file.txt s3://$AWS_BUCKET --region $AWS_REGION
