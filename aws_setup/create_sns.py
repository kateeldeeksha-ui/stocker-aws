"""
aws_setup/create_sns.py
Creates 2 SNS topics:
  1. User Account Topic  — for signup/login notifications
  2. Transaction Topic   — for buy/sell notifications
Run: python aws_setup/create_sns.py --email you@example.com
"""
import boto3, argparse, os

REGION = os.environ.get('AWS_REGION', 'us-east-1')

def setup_sns(email):
    sns = boto3.client('sns', region_name=REGION)

    # Topic 1: User Account
    r1   = sns.create_topic(Name='stocker-user-account')
    arn1 = r1['TopicArn']
    print(f"✅ User Account Topic ARN: {arn1}")

    # Topic 2: Transactions
    r2   = sns.create_topic(Name='stocker-transactions')
    arn2 = r2['TopicArn']
    print(f"✅ Transaction Topic ARN:  {arn2}")

    if email:
        sns.subscribe(TopicArn=arn1, Protocol='email', Endpoint=email)
        sns.subscribe(TopicArn=arn2, Protocol='email', Endpoint=email)
        print(f"\n📧 Check {email} inbox to confirm both subscriptions!")

    print(f"\n📋 Add these to your .env file:")
    print(f"USER_ACCOUNT_TOPIC_ARN={arn1}")
    print(f"TRANSACTION_TOPIC_ARN={arn2}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', default='', help='Email for notifications')
    args = parser.parse_args()
    setup_sns(args.email)
