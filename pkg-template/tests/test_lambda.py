
import json
import os
import boto3

client = boto3.client('lambda')

# payload
d = {
    'bucket_name': 'meza-test',
    'image_id': '04fb1234-2833-40cb-b80c-e9f6281ec023'
}
s = json.dumps(d)

# invoke
response = client.invoke(
    FunctionName='meza-sharder',
    Payload=s
)

# parse response
statusCode = response['StatusCode']
payload = json.loads(response['Payload'].read().decode())

print(f'Status Code : {statusCode}\n')
print(payload)
