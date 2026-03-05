"""
aws_setup/create_tables.py
Creates all 4 DynamoDB tables exactly as per the ER diagram.
Run: python aws_setup/create_tables.py
"""
import boto3, os

REGION = os.environ.get('AWS_REGION', 'us-east-1')
client = boto3.client('dynamodb', region_name=REGION)

TABLES = [
    # Users table — partition key: email
    {
        'TableName': 'stocker_users',
        'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'email', 'AttributeType': 'S'}],
        'BillingMode': 'PAY_PER_REQUEST',
    },
    # Stocks table — partition key: id
    {
        'TableName': 'stocker_stocks',
        'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}],
        'BillingMode': 'PAY_PER_REQUEST',
    },
    # Portfolio table — partition key: user_id, sort key: stock_id
    {
        'TableName': 'stocker_portfolio',
        'KeySchema': [
            {'AttributeName': 'user_id',  'KeyType': 'HASH'},
            {'AttributeName': 'stock_id', 'KeyType': 'RANGE'},
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'user_id',  'AttributeType': 'S'},
            {'AttributeName': 'stock_id', 'AttributeType': 'S'},
        ],
        'BillingMode': 'PAY_PER_REQUEST',
    },
    # Transactions table — partition key: id
    {
        'TableName': 'stocker_transactions',
        'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}],
        'BillingMode': 'PAY_PER_REQUEST',
    },
]

def create_tables():
    existing = client.list_tables()['TableNames']
    for spec in TABLES:
        name = spec['TableName']
        if name in existing:
            print(f"  ✓ {name} already exists — skipping.")
        else:
            client.create_table(**spec)
            print(f"  ✅ Created: {name}")

if __name__ == '__main__':
    print("Creating DynamoDB tables...")
    create_tables()
    print("\nAll done! Tables created:")
    print("  • stocker_users        (id, username, email, password, role, is_active)")
    print("  • stocker_stocks       (id, symbol, name, price, market_cap, sector, industry)")
    print("  • stocker_portfolio    (id, user_id, stock_id, quantity, average_price)")
    print("  • stocker_transactions (id, user_id, stock_id, action, price, quantity, status)")
