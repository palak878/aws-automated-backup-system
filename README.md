markdown

\# AWS Automated Backup \& Disaster Recovery System



An automated, serverless backup pipeline built on AWS that takes scheduled EBS snapshots of an EC2 instance, logs every run for auditing, sends real-time email alerts, and displays backup history through a Dockerized Flask dashboard.



\---



\## Overview



Manually backing up servers is error-prone and easy to forget. This project automates the entire process end-to-end using AWS-native serverless services — with monitoring, alerting, and a visual dashboard — while staying entirely within the AWS Free Tier.



\*\*Core idea:\*\* every night, a scheduled job automatically snapshots a server's disk, records the result, and notifies the owner — whether it succeeds or fails — with no manual intervention.



\---



\## Architecture



EventBridge (daily cron trigger, 2:00 AM IST)

|

v

AWS Lambda (Python)

|

+--> EC2 / EBS -> creates a snapshot of the attached volume

|

+--> DynamoDB -> logs the run (timestamp, snapshot ID, status)

|

+--> SNS -> sends a success/failure email notification

|

v

CloudWatch Alarm (watches Lambda errors,

also notifies via the same SNS topic)



DynamoDB --> Flask Dashboard (Dockerized) -> displays backup history \& stats





\---



\## Tech Stack



| Layer | Technology |

|---|---|

| Compute (target) | AWS EC2 |

| Backup engine | AWS Lambda (Python 3.12, boto3) |

| Scheduling | Amazon EventBridge (cron) |

| Storage / snapshots | Amazon EBS Snapshots, Amazon S3 (lifecycle policies) |

| Audit logging | Amazon DynamoDB |

| Alerting | Amazon SNS (email) |

| Monitoring | Amazon CloudWatch Alarms |

| Dashboard | Flask (Python), Jinja2 |

| Containerization | Docker |

| IAM | Custom least-privilege-aware IAM role for Lambda |



\---



\## Features



\- \*\*Fully automated daily backups\*\* — no manual trigger needed once deployed

\- \*\*Audit trail\*\* — every backup attempt (success or failure) is logged with a timestamp, snapshot ID, and volume ID

\- \*\*Email alerts\*\* — instant notification via SNS whenever a backup succeeds or fails

\- \*\*Error monitoring\*\* — a CloudWatch Alarm catches Lambda-level failures (timeouts, crashes) independent of the backup logic itself

\- \*\*Cost-safe by design\*\* — a zero-spend AWS Budget alert, and an S3 lifecycle rule that expires old objects after 90 days

\- \*\*Visual dashboard\*\* — a Flask web app showing total/successful/failed backup counts and a full history table, containerized with Docker

\- \*\*Free-tier friendly\*\* — every service used (Lambda, DynamoDB on-demand, SNS, EventBridge, S3) stays within AWS Free Tier limits at this scale



\---



\## How It Works



1\. \*\*EventBridge\*\* triggers the Lambda function daily via a cron expression (`30 20 \* \* ? \*` — this is 20:30 UTC, i.e., 2:00 AM IST).

2\. \*\*Lambda\*\* looks up the EBS volume attached to the target EC2 instance and creates a snapshot of it.

3\. On success, Lambda writes a record to \*\*DynamoDB\*\* (`BackupAuditLog` table) with the snapshot ID, volume ID, and timestamp, then publishes a success message via \*\*SNS\*\*.

4\. On failure (e.g., instance not found, volume detached), Lambda logs a `FAILED` record with the error message and sends a failure alert via SNS.

5\. A \*\*CloudWatch Alarm\*\* independently watches the Lambda function's `Errors` metric, so even a hard crash (not just a caught exception) triggers a notification.

6\. The \*\*Flask dashboard\*\* reads all records from DynamoDB and displays them as a stat summary (total/success/failed) plus a sortable history table.



\---



\## Project Structure



backup-dashboard/

├── app.py # Flask application

├── templates/

│ └── dashboard.html # Dashboard UI (Jinja2 template)

├── requirements.txt # Python dependencies (flask, boto3)

├── Dockerfile # Container build definition

└── .gitignore # Excludes venv, credentials, and cache files





Lambda function code (`automated-backup-function`) is maintained directly in the AWS Console / Lambda source and is included here as reference (see below).



\---



\## Setup \& Deployment



\### Prerequisites

\- An AWS account (Free Tier eligible)

\- Python 3.10+

\- Docker Desktop

\- AWS CLI configured (`aws configure`) with an IAM user (not root)



\### 1. AWS Infrastructure

Set up in the AWS Console (all in a single region, e.g., `ap-south-1`):

1\. An EC2 instance (`t2.micro` / `t3.micro`) — the backup target

2\. An IAM role (`backup-lambda-role`) with permissions for EC2, S3, DynamoDB, CloudWatch Logs, and SNS

3\. A DynamoDB table `BackupAuditLog` (partition key: `backup\_id`, String)

4\. An S3 bucket with a 90-day expiration lifecycle rule

5\. A Lambda function (`automated-backup-function`, Python 3.12) using the role above

6\. An EventBridge scheduled rule targeting the Lambda function

7\. An SNS topic (`backup-alerts`) with an email subscription

8\. A CloudWatch Alarm on the Lambda function's `Errors` metric, notifying the same SNS topic



\### 2. Lambda Function



```python

import boto3

import datetime

import uuid



ec2 = boto3.client('ec2', region\_name='ap-south-1')

dynamodb = boto3.resource('dynamodb', region\_name='ap-south-1')

sns = boto3.client('sns', region\_name='ap-south-1')

table = dynamodb.Table('BackupAuditLog')



INSTANCE\_ID = '<your-ec2-instance-id>'

SNS\_TOPIC\_ARN = '<your-sns-topic-arn>'



def lambda\_handler(event, context):

&#x20;   backup\_id = str(uuid.uuid4())

&#x20;   timestamp = datetime.datetime.utcnow().isoformat()



&#x20;   try:

&#x20;       volumes = ec2.describe\_volumes(

&#x20;           Filters=\[{'Name': 'attachment.instance-id', 'Values': \[INSTANCE\_ID]}]

&#x20;       )

&#x20;       volume\_id = volumes\['Volumes']\[0]\['VolumeId']



&#x20;       snapshot = ec2.create\_snapshot(

&#x20;           VolumeId=volume\_id,

&#x20;           Description=f'Automated backup {timestamp}'

&#x20;       )

&#x20;       snapshot\_id = snapshot\['SnapshotId']



&#x20;       table.put\_item(Item={

&#x20;           'backup\_id': backup\_id,

&#x20;           'timestamp': timestamp,

&#x20;           'snapshot\_id': snapshot\_id,

&#x20;           'volume\_id': volume\_id,

&#x20;           'status': 'SUCCESS'

&#x20;       })



&#x20;       sns.publish(

&#x20;           TopicArn=SNS\_TOPIC\_ARN,

&#x20;           Subject='Backup Succeeded',

&#x20;           Message=f'Backup completed successfully.\\nSnapshot ID: {snapshot\_id}\\nTime: {timestamp}'

&#x20;       )



&#x20;       return {'statusCode': 200, 'body': f'Snapshot {snapshot\_id} created successfully'}



&#x20;   except Exception as e:

&#x20;       table.put\_item(Item={

&#x20;           'backup\_id': backup\_id,

&#x20;           'timestamp': timestamp,

&#x20;           'status': 'FAILED',

&#x20;           'error': str(e)

&#x20;       })



&#x20;       sns.publish(

&#x20;           TopicArn=SNS\_TOPIC\_ARN,

&#x20;           Subject='Backup FAILED',

&#x20;           Message=f'Backup failed.\\nError: {str(e)}\\nTime: {timestamp}'

&#x20;       )



&#x20;       raise e

```



\### 3. Run the Dashboard Locally

```bash

python -m venv venv

venv\\Scripts\\activate        # Windows

\# source venv/bin/activate   # macOS/Linux



pip install -r requirements.txt

aws configure                # enter IAM access key, secret, region (ap-south-1), output format (json)



python app.py

```

Visit `http://localhost:5000`.



\### 4. Run the Dashboard in Docker

```bash

docker build -t backup-dashboard .

docker run -p 5000:5000 -v \~/.aws:/root/.aws:ro backup-dashboard

```

Visit `http://localhost:5000`.



\---



\## Known Limitations \& Next Steps



Being upfront about what this version doesn't yet handle — and what a more mature version would add:



\- \*\*No snapshot completion polling\*\* — the Lambda triggers `create\_snapshot` and logs success immediately, without confirming the snapshot reaches `completed` status (large volumes can take time).

\- \*\*No snapshot retention/cleanup policy\*\* — EBS snapshots accumulate daily; a pruning Lambda (e.g., keep last 7 daily + 4 weekly) is needed to control long-term storage cost.

\- \*\*Overly broad IAM permissions\*\* — the Lambda role currently uses full-access managed policies (`AmazonEC2FullAccess`, etc.) for development speed. Production use should scope this down to specific actions and resource ARNs (least privilege).

\- \*\*DynamoDB dashboard uses a full table scan\*\* — fine at small scale, but would need a Global Secondary Index (e.g., on `status` or `timestamp`) to stay efficient as records grow.

\- \*\*Local AWS credentials mounted into Docker\*\* — acceptable for local development; in a real EC2 deployment, this should be replaced with an IAM Instance Profile attached to the instance instead of mounted credential files.

\- \*\*No cross-region backup replication\*\* — currently single-region; a disaster-recovery-complete version would replicate critical snapshots/S3 objects to a second AWS region.

\- \*\*CI/CD deployment to EC2 not yet wired up\*\* — the dashboard is built and Dockerized but not yet deployed via a pipeline (e.g., Jenkins) to a live EC2 instance.



\---



\## Cost Safety Measures



\- Zero-spend AWS Budget alert — triggers an email if any charge occurs

\- S3 lifecycle rule — expires objects after 90 days

\- All services (Lambda, DynamoDB on-demand, SNS, EventBridge) used well within AWS Free Tier limits at this project's scale



\---



\## Author



\*\*Palak\*\* GitHub: \[github.com/palak878](https://github.com/palak878)

