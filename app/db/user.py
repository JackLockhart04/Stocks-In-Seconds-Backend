# app/db/users.py

from app.db.dynamo_client import get_dynamodb_resource

dynamodb = get_dynamodb_resource()

class User:
    def __init__(self, table_name, email=None, username=None, last_login=None):
        self.table = dynamodb.Table(table_name)  # Use the provided table name
        self.email = email
        self.username = username
        self.last_login = last_login  # Default value
    
    @classmethod
    def create_table(cls, table_name):
        try:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'email', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )
            table.wait_until_exists()
            print(f"Table {table_name} created successfully.")
        except dynamodb.meta.client.exceptions.ResourceInUseException:
            print(f"Table {table_name} already exists.")

    @classmethod
    def get(cls, table_name, email):
        table = dynamodb.Table(table_name)
        try:
            response = table.get_item(Key={'email': email})

            if 'Item' in response:
                item = response['Item']
                return User(
                    table_name=table_name,
                    email=item['email'],
                    username=item['username'],
                    last_login=item['last_login']
                )
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")  # Detailed error message
            return None

    def add(self):
        self.table.put_item(
            Item={
                'email': self.email,
                'username': self.username,
                'last_login': self.last_login
            }
        )

    # def update(self, **kwargs):
    #     update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in kwargs.keys())
    #     expression_attribute_values = {f":{k}": v for k, v in kwargs.items()}
    #     self.table.update_item(
    #         Key={'email': self.email},
    #         UpdateExpression=update_expression,
    #         ExpressionAttributeValues=expression_attribute_values
    #     )
    #     for k, v in kwargs.items():
    #         setattr(self, k, v)
            
    def update(self, updates):
        update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in updates.keys())
        expression_attribute_values = {f":{k}": v for k, v in updates.items()}
        
        self.table.update_item(
            Key={'email': self.email},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

    def delete(self):
        self.table.delete_item(Key={'email': self.email})