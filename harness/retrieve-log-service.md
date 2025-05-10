### Retrieval Log Process

1. Get the Log Service Token
The first step is to obtain a Log Service token using the /log-service/token endpoint:

```bash
curl -X GET \
  'https://app.harness.io/gateway/log-service/token?accountID=YOUR_ACCOUNT_ID&routingId=YOUR_ACCOUNT_ID' \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: YOUR_API_KEY'
```
This request returns a special token specifically for accessing the log service.

2. Request Log Download with the Token
Use the token to request a download URL for the logs via the /log-service/blob/download endpoint:

```bash
curl -X POST \
  'https://app.harness.io/gateway/log-service/blob/download?accountID=YOUR_ACCOUNT_ID&prefix=YOUR_LOG_KEY' \
  -H 'Content-Type: application/json' \
  -H 'x-harness-token: YOUR_LOG_SERVICE_TOKEN'
```

Where: YOUR_LOG_KEY is the key obtained from getDownloadLogKeyFromFqn, with a format like: accountId/orgId/projectId/pipelineId/runSequence/level0:stepName

3. Download the Log File
Finally, use the download URL returned in the previous response:

```bash
curl -X GET \
  'DOWNLOAD_URL_FROM_PREVIOUS_RESPONSE' \
  -o logs.zip
```
This downloads a zip file containing the logs for the specified step.

#### Complete Flow Summary
- The system gets a log key for a specific pipeline execution step
- It obtains a special log service token using the /log-service/token endpoint
- It uses that token to request a download URL through the /log-service/blob/download endpoint
- The system polls the download URL until the logs are ready (with retry logic)
- Finally, it downloads the logs as a zip file and processes them for validation
