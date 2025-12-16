# ResearchAnalyst AWS Infrastructure Setup Guide

Complete guide to setting up RDS PostgreSQL, S3, and OpenSearch for the ResearchAnalyst backend.

---

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Python 3.8+** installed
4. **Required Python packages**:
   ```bash
   pip install boto3 opensearch-py requests-aws4auth psycopg2-binary
   ```

---

## 1. RDS PostgreSQL Setup

### Step 1.1: Create RDS PostgreSQL Instance

**Option A: Using AWS Console**

1. Go to [AWS RDS Console](https://console.aws.amazon.com/rds/)
2. Click **Create database**
3. Choose:
   - **Engine**: PostgreSQL 15.x or 14.x
   - **Template**: Free tier (for testing) or Production (for live)
   - **DB instance identifier**: `researchanalyst-db`
   - **Master username**: `postgres`
   - **Master password**: (save this securely!)
4. Instance configuration:
   - **DB instance class**: db.t3.micro (free tier) or db.t3.medium (production)
   - **Storage**: 20 GB GP3, enable autoscaling to 100 GB
5. Connectivity:
   - **VPC**: Default or your custom VPC
   - **Public access**: Yes (for initial setup, restrict later)
   - **VPC security group**: Create new, allow PostgreSQL (5432) from your IP
6. Additional configuration:
   - **Initial database name**: `researchanalyst`
   - **Backup retention**: 7 days
   - **Enable automated backups**: Yes
7. Click **Create database**

**Option B: Using AWS CLI**

```bash
aws rds create-db-instance \
    --db-instance-identifier researchanalyst-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password YOUR_SECURE_PASSWORD \
    --allocated-storage 20 \
    --storage-type gp3 \
    --db-name researchanalyst \
    --vpc-security-group-ids sg-xxxxxxxx \
    --backup-retention-period 7 \
    --publicly-accessible \
    --enable-cloudwatch-logs-exports '["postgresql"]' \
    --tags Key=Project,Value=ResearchAnalyst
```

### Step 1.2: Wait for RDS Instance to be Available

```bash
aws rds wait db-instance-available --db-instance-identifier researchanalyst-db
```

### Step 1.3: Get Connection Details

```bash
aws rds describe-db-instances \
    --db-instance-identifier researchanalyst-db \
    --query 'DBInstances[0].[Endpoint.Address,Endpoint.Port,MasterUsername]' \
    --output table
```

Save the endpoint (e.g., `researchanalyst-db.xxxxxx.us-east-1.rds.amazonaws.com`)

### Step 1.4: Run Database Migration

```bash
# Test connection first
psql -h researchanalyst-db.xxxxxx.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d researchanalyst \
     -p 5432

# Run migration script
psql -h researchanalyst-db.xxxxxx.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d researchanalyst \
     -p 5432 \
     -f db_migration.sql
```

### Step 1.5: Verify Tables Created

```bash
psql -h researchanalyst-db.xxxxxx.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d researchanalyst \
     -c "\dt"
```

Expected tables:
- users
- companies
- watchlists
- watchlist_items
- concalls
- files

---

## 2. S3 Bucket Setup

### Step 2.1: Configure the Script

Edit `s3_setup.py` and set:
```python
BUCKET_NAME = "researchanalyst-storage"
REGION = "us-east-1"  # Your preferred region
```

### Step 2.2: Run Setup Script

```bash
python s3_setup.py
```

This will:
- ✓ Create S3 bucket
- ✓ Enable versioning
- ✓ Enable encryption (AES256)
- ✓ Block all public access
- ✓ Configure CORS for frontend
- ✓ Set up lifecycle policies
- ✓ Create folder structure:
  - `transcripts/`
  - `audio/`
  - `company-outputs/`
  - `sector-outputs/`
  - `exports/`
  - `logs/app/`

### Step 2.3: Verify Bucket

```bash
aws s3 ls s3://researchanalyst-storage/
```

---

## 3. OpenSearch Setup

### Step 3.1: Create OpenSearch Domain

**Option A: Using AWS Console**

1. Go to [Amazon OpenSearch Console](https://console.aws.amazon.com/aos/)
2. Click **Create domain**
3. Choose:
   - **Deployment type**: Development and testing (1 node) or Production (3 nodes)
   - **Domain name**: `researchanalyst-search`
   - **Engine version**: OpenSearch 2.11 or latest
4. Instance configuration:
   - **Instance type**: t3.small.search (free tier eligible)
   - **Number of nodes**: 1 (dev) or 3 (production)
   - **Data nodes**: 10 GB EBS storage per node
5. Network:
   - **Network**: VPC access (recommended) or Public access
   - **VPC**: Select your VPC and subnets
   - **Security groups**: Allow HTTPS (443) from Lambda/EC2
6. Access policy:
   - Fine-grained access control: Enabled
   - Master user: Create (save credentials!)
7. Click **Create**

**Option B: Using AWS CLI**

```bash
aws opensearch create-domain \
    --domain-name researchanalyst-search \
    --engine-version OpenSearch_2.11 \
    --cluster-config InstanceType=t3.small.search,InstanceCount=1 \
    --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=10 \
    --access-policies '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {"AWS": "*"},
        "Action": "es:*",
        "Resource": "arn:aws:es:us-east-1:ACCOUNT_ID:domain/researchanalyst-search/*"
      }]
    }' \
    --tags Key=Project,Value=ResearchAnalyst
```

### Step 3.2: Wait for Domain to be Active

```bash
aws opensearch describe-domain \
    --domain-name researchanalyst-search \
    --query 'DomainStatus.Processing' \
    --output text
```

Wait until it returns `false` (typically 10-15 minutes)

### Step 3.3: Get OpenSearch Endpoint

```bash
aws opensearch describe-domain \
    --domain-name researchanalyst-search \
    --query 'DomainStatus.Endpoint' \
    --output text
```

Save endpoint (e.g., `search-researchanalyst-search-abc123.us-east-1.es.amazonaws.com`)

### Step 3.4: Configure and Run Setup Script

Edit `opensearch_setup.py` and set:
```python
OPENSEARCH_ENDPOINT = "search-researchanalyst-search-abc123.us-east-1.es.amazonaws.com"
REGION = "us-east-1"
```

Run the script:
```bash
python opensearch_setup.py
```

This will:
- ✓ Create `companies_v1` index
- ✓ Configure analyzers for fuzzy search
- ✓ Set up field mappings
- ✓ Insert sample documents (optional)
- ✓ Test search functionality

### Step 3.5: Verify Index

```bash
curl -XGET "https://OPENSEARCH_ENDPOINT/companies_v1/_search?pretty" \
     -u "master-user:password"
```

---

## 4. Environment Variables

Create a `.env` file or export these variables:

```bash
# Database
export DB_HOST="researchanalyst-db.xxxxxx.us-east-1.rds.amazonaws.com"
export DB_PORT="5432"
export DB_USER="postgres"
export DB_PASSWORD="your_secure_password"
export DB_NAME="researchanalyst"

# S3
export S3_BUCKET="researchanalyst-storage"
export AWS_REGION="us-east-1"

# OpenSearch
export OPENSEARCH_ENDPOINT="search-researchanalyst-search-abc123.us-east-1.es.amazonaws.com"

# Cognito (set these later after creating Cognito User Pool)
export COGNITO_REGION="us-east-1"
export COGNITO_USER_POOL_ID="us-east-1_xxxxxxxxx"

# TijoriStack API
export TIJORISTACK_API_KEY="your_api_key"
export TIJORISTACK_BASE_URL="https://www.tijoristack.ai/api/v1"

# LLM (Gemini, OpenAI, etc.)
export LLM_API_KEY="your_llm_api_key"
```

---

## 5. AWS IAM Permissions

### For Lambda Functions

Create an IAM role with these policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::researchanalyst-storage",
        "arn:aws:s3:::researchanalyst-storage/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "es:ESHttpGet",
        "es:ESHttpPost",
        "es:ESHttpPut",
        "es:ESHttpDelete"
      ],
      "Resource": "arn:aws:es:us-east-1:ACCOUNT_ID:domain/researchanalyst-search/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### For RDS Access

Ensure Lambda functions are in the same VPC as RDS or configure VPC peering.

---

## 6. Security Hardening (Production)

### RDS Security

1. **Restrict public access**:
   ```bash
   aws rds modify-db-instance \
       --db-instance-identifier researchanalyst-db \
       --no-publicly-accessible \
       --apply-immediately
   ```

2. **Enable SSL/TLS**:
   - Download RDS CA certificate
   - Configure connection string with `sslmode=require`

3. **Create read-only user** for analytics:
   ```sql
   CREATE USER readonly WITH PASSWORD 'password';
   GRANT CONNECT ON DATABASE researchanalyst TO readonly;
   GRANT USAGE ON SCHEMA public TO readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
   ```

### S3 Security

1. **Update CORS** to restrict to your domain:
   ```python
   'AllowedOrigins': ['https://app.researchanalyst.io']
   ```

2. **Enable access logging**:
   ```bash
   aws s3api put-bucket-logging \
       --bucket researchanalyst-storage \
       --bucket-logging-status file://logging.json
   ```

### OpenSearch Security

1. **Enable fine-grained access control**
2. **Use VPC endpoints** instead of public access
3. **Configure IP allowlists** in access policy

---

## 7. Monitoring & Alerting

### CloudWatch Alarms

```bash
# RDS CPU Utilization
aws cloudwatch put-metric-alarm \
    --alarm-name researchanalyst-db-high-cpu \
    --alarm-description "Alert when RDS CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=researchanalyst-db

# S3 Bucket Size
aws cloudwatch put-metric-alarm \
    --alarm-name researchanalyst-s3-size \
    --alarm-description "Alert when S3 bucket exceeds 100GB" \
    --metric-name BucketSizeBytes \
    --namespace AWS/S3 \
    --statistic Average \
    --period 86400 \
    --threshold 107374182400 \
    --comparison-operator GreaterThanThreshold
```

---

## 8. Testing the Setup

### Test Database Connection

```bash
python -c "
import psycopg2
conn = psycopg2.connect(
    host='YOUR_RDS_ENDPOINT',
    database='researchanalyst',
    user='postgres',
    password='YOUR_PASSWORD'
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM users;')
print('Database connected:', cur.fetchone())
conn.close()
"
```

### Test S3 Access

```bash
python -c "
import boto3
s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket='researchanalyst-storage', MaxKeys=5)
print('S3 connected:', response.get('Name'))
"
```

### Test OpenSearch

```bash
python -c "
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, 'us-east-1', 'es')

client = OpenSearch(
    hosts=[{'host': 'YOUR_OPENSEARCH_ENDPOINT', 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    connection_class=RequestsHttpConnection
)
print('OpenSearch connected:', client.info())
"
```

---

## 9. Cost Estimation (Monthly)

### Free Tier (First 12 months)
- **RDS**: db.t3.micro (750 hrs) - $0
- **S3**: 5 GB storage - $0
- **OpenSearch**: t3.small.search (750 hrs) - $0
- **Estimated**: $0 - $10/month

### Production (After free tier)
- **RDS**: db.t3.medium (24/7) - ~$60/month
- **S3**: 100 GB + requests - ~$5/month
- **OpenSearch**: t3.small.search x3 (HA) - ~$150/month
- **Data Transfer**: ~$10/month
- **Estimated**: $225 - $250/month

---

## 10. Troubleshooting

### RDS Connection Issues

```bash
# Check security group
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# Test connection from EC2/Lambda
nc -zv YOUR_RDS_ENDPOINT 5432
```

### S3 Access Denied

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket researchanalyst-storage

# Check IAM permissions
aws iam simulate-principal-policy \
    --policy-source-arn arn:aws:iam::ACCOUNT:user/USERNAME \
    --action-names s3:GetObject \
    --resource-arns arn:aws:s3:::researchanalyst-storage/*
```

### OpenSearch Connection Failed

```bash
# Check domain status
aws opensearch describe-domain --domain-name researchanalyst-search

# Test endpoint
curl -XGET "https://YOUR_OPENSEARCH_ENDPOINT/_cluster/health?pretty"
```

---

## 11. Backup & Disaster Recovery

### RDS Backups

```bash
# Create manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier researchanalyst-db \
    --db-snapshot-identifier researchanalyst-backup-$(date +%Y%m%d)

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier researchanalyst-db-restored \
    --db-snapshot-identifier researchanalyst-backup-20251207
```

### S3 Versioning

Already enabled via setup script. To restore a file:

```bash
# List versions
aws s3api list-object-versions \
    --bucket researchanalyst-storage \
    --prefix transcripts/

# Restore specific version
aws s3api copy-object \
    --bucket researchanalyst-storage \
    --copy-source researchanalyst-storage/transcripts/file.json?versionId=VERSION_ID \
    --key transcripts/file.json
```

### OpenSearch Snapshots

Configure automated snapshots via AWS console or create manual snapshots.

---

## Summary Checklist

- [ ] RDS PostgreSQL instance created and accessible
- [ ] Database schema migrated successfully
- [ ] S3 bucket created with proper structure and policies
- [ ] OpenSearch domain created and index configured
- [ ] Environment variables documented
- [ ] IAM roles and policies configured
- [ ] Security hardening applied
- [ ] Monitoring and alarms set up
- [ ] Backup strategy implemented
- [ ] All services tested and verified

---

**Need Help?** 
- AWS RDS: https://docs.aws.amazon.com/rds/
- AWS S3: https://docs.aws.amazon.com/s3/
- Amazon OpenSearch: https://docs.aws.amazon.com/opensearch-service/

