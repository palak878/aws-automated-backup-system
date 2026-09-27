# AWS Automated Backup & Disaster Recovery System

An automated, serverless backup pipeline built on AWS that creates scheduled EBS snapshots of an EC2 instance, logs every backup for auditing, sends real-time email alerts, and displays backup history through a Dockerized Flask dashboard.

---

## Project Overview

Manually backing up cloud servers is time-consuming and prone to human error. This project automates the complete backup workflow using AWS serverless services, ensuring backups happen every day without manual intervention.

**Core Idea:** Every night at **2:00 AM IST**, AWS automatically creates a snapshot of an EC2 instance's EBS volume, stores backup details in DynamoDB, sends an email notification through SNS, and displays backup history on a Flask dashboard.

---

## Architecture

```text
                    Amazon EventBridge
              (Daily Cron - 2:00 AM IST)
                         │
                         ▼
                AWS Lambda (Python)
                         │
     ┌───────────────────┼────────────────────┐
     ▼                   ▼                    ▼
 Amazon EC2         Amazon DynamoDB       Amazon SNS
 + EBS Volume       BackupAuditLog        Email Alerts
 (Create Snapshot)  (Audit Records)     (Success/Failure)
                         │
                         ▼
                 Flask Dashboard (Docker)
        Backup Statistics + History + Logs

        CloudWatch Alarm monitors Lambda Errors
                  │
                  ▼
           Sends SNS Notification
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Compute | AWS EC2 |
| Backup Engine | AWS Lambda (Python 3.12, boto3) |
| Scheduling | Amazon EventBridge |
| Storage | Amazon EBS Snapshots, Amazon S3 |
| Audit Logging | Amazon DynamoDB |
| Notifications | Amazon SNS |
| Monitoring | Amazon CloudWatch |
| Dashboard | Flask, Jinja2 |
| Containerization | Docker |
| Security | AWS IAM |

---

## Features

- Automated daily EBS backups using EventBridge Scheduler.
- Serverless backup execution with AWS Lambda.
- Backup audit logging in DynamoDB.
- Success and failure email notifications through SNS.
- CloudWatch alarm for Lambda runtime failures.
- Dockerized Flask dashboard with backup statistics and history.
- AWS Free Tier friendly architecture.
- Cost monitoring with AWS Budget alerts and S3 Lifecycle Rules.

---

## How It Works

1. **EventBridge** triggers the Lambda function every day at **2:00 AM IST**.
2. **Lambda** identifies the EBS volume attached to the EC2 instance and creates a snapshot.
3. Backup details are stored in **DynamoDB** (`BackupAuditLog` table).
4. **SNS** sends a success or failure email notification.
5. **CloudWatch Alarm** monitors Lambda errors and sends alerts for crashes or timeouts.
6. The **Flask Dashboard** reads DynamoDB records and displays backup history and statistics.

---

## Project Structure

```text
aws-automated-backup-disaster-recovery/
│
├── README.md
├── app.py
├── lambda_function.py
├── requirements.txt
├── Dockerfile
├── .gitignore
│
└── templates/
    └── dashboard.html
```

---

## Setup & Deployment

### Prerequisites

- AWS Free Tier account
- Python 3.10+
- Docker Desktop
- AWS CLI configured with IAM credentials

### Run Locally

```bash
git clone https://github.com/palak878/aws-automated-backup-disaster-recovery.git

cd aws-automated-backup-disaster-recovery

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

aws configure

python app.py
```

Open: `http://localhost:5000`

### Run with Docker

```bash
docker build -t backup-dashboard .

docker run -p 5000:5000 -v ~/.aws:/root/.aws:ro backup-dashboard
```

Open: `http://localhost:5000`

---

## AWS Services Used

- Amazon EC2
- Amazon EBS Snapshots
- AWS Lambda
- Amazon EventBridge
- Amazon DynamoDB
- Amazon SNS
- Amazon CloudWatch
- Amazon S3
- AWS IAM

---

## Cost Optimization

- AWS Budget alert for zero spending.
- S3 lifecycle policy deletes old objects after 90 days.
- Lambda, EventBridge, DynamoDB, and SNS remain within AWS Free Tier limits for this project.

---

## Current Limitations

- Snapshot completion is not verified before logging success.
- Old EBS snapshots are not deleted automatically.
- Dashboard uses a full DynamoDB table scan.
- Local Docker uses mounted AWS credentials.
- Single-region backup only.

---

## Future Improvements

- Snapshot retention policy (7 daily + 4 weekly backups).
- Cross-region disaster recovery replication.
- Least-privilege IAM policies.
- CI/CD deployment using GitHub Actions or Jenkins.
- Snapshot completion polling before logging success.
- Backup analytics dashboard with storage usage trends.

---

## Learning Outcomes

This project demonstrates hands-on experience with:

- AWS Lambda
- Amazon EC2 & EBS Snapshots
- Amazon EventBridge Scheduler
- Amazon DynamoDB
- Amazon SNS
- Amazon CloudWatch Alarms
- AWS IAM
- Flask
- Docker

---

## Author

**Palak Prasad**

- GitHub: https://github.com/palak878
- Electronics & Telecommunication Engineering Student | Cloud & DevOps Enthusiast
