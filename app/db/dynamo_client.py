# app/db/dynamo_client.py

import boto3

# Initialize a session using boto3
session = boto3.Session()

# Use the session to create a DynamoDB resource
dynamodb = session.resource('dynamodb', region_name='us-east-2')

def get_dynamodb_resource():
    return dynamodb