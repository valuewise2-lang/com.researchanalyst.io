# ResearchAnalyst AWS Setup - Complete Summary

## 🎯 What You Have Now

I've created all the files you need to set up your AWS infrastructure. Here's what's ready:

### 📁 Files Created

1. **`db_migration.sql`** - Complete PostgreSQL schema
2. **`cloudshell_setup.sh`** - Database setup script
3. **`cloudshell_setup_s3.sh`** - S3 bucket setup script
4. **`setup_all.sh`** - All-in-one setup script ⭐ **USE THIS**
5. **`CLOUDSHELL_QUICKSTART.md`** - Step-by-step guide
6. **`AWS_SETUP_GUIDE.md`** - Complete documentation
7. **`fix_rds_security.py`** - Security group helper (local)
8. **`run_migration.py`** - Migration runner (local)
9. **`requirements_aws.txt`** - Python dependencies

---

## 🚀 Quick Start (CloudShell Method - Recommended)

### 1. Open AWS CloudShell

1. Login to AWS Console
2. Switch to region: **ap-south-1** (Mumbai)
3. Click CloudShell icon (>_) in top navigation

### 2. Upload Files

In CloudShell, click **Actions** → **Upload file** and upload:
- `db_migration.sql`
- `setup_all.sh`

### 3. Run Setup

```bash
# Make script executable
chmod +x setup_all.sh

# Run complete setup
./setup_all.sh
```

That's it! The script will:
- ✅ Install PostgreSQL client
- ✅ Create all 6 database tables
- ✅ Setup S3 bucket with folders
- ✅ Configure encryption, versioning, CORS
- ✅ Generate `.env` configuration file
- ✅ Create test scripts

---

## 📊 Your Current Setup

### RDS PostgreSQL
- **Endpoint:** `researchanalyst-db.cle6mqs82txq.ap-south-1.rds.amazonaws.com`
- **Port:** `5432`
- **Database:** `researchanalyst`
- **User:** `postgres`
- **Password:** `Nokia#5300`
- **Region:** `ap-south-1`

### Tables Created (6 total)
1. `users` - User accounts & auth
2. `companies` - Company directory (ISIN-based)
3. `watchlists` - User watchlists (NORMAL/SECTOR)
4. `watchlist_items` - Stocks in watchlists
5. `concalls` - Conference call events
6. `files` - S3 file references

### S3 Bucket
- **Name:** `researchanalyst-storage`
- **Region:** `ap-south-1`
- **Folders:**
  - `transcripts/` - Call transcripts
  - `audio/` - Audio recordings
  - `company-outputs/` - Analysis outputs
  - `sector-outputs/` - Sector analyses
  - `exports/` - User exports (7-day TTL)
  - `logs/app/` - Application logs

---

## 🔧 What's Still Needed

### 1. OpenSearch Domain

**Create in AWS Console:**
1. Go to: https://ap-south-1.console.aws.amazon.com/aos/home
2. Create domain: `researchanalyst-search`
3. Instance: `t3.small.search` (1 node for dev)
4. Storage: 10 GB
5. Access: Public (for now) or VPC
6. Wait 10-15 minutes

**Then create index in CloudShell:**
```bash
OPENSEARCH_ENDPOINT="your-endpoint-here.ap-south-1.es.amazonaws.com"

curl -XPUT "https://${OPENSEARCH_ENDPOINT}/companies_v1" \
  -H 'Content-Type: application/json' \
  -d @opensearch_mapping.json
```

### 2. Cognito User Pool

**Create for authentication:**
1. Go to: https://ap-south-1.console.aws.amazon.com/cognito/
2. Create User Pool: `researchanalyst-users`
3. Enable Hosted UI
4. Configure app client
5. Copy User Pool ID and Client ID to `.env`

### 3. API Keys

Update in `.env` file:
- `TIJORISTACK_API_KEY` - Get from TijoriStack
- `LLM_API_KEY` - OpenAI/Gemini API key

---

## ✅ Verification Steps

### Test Database
```bash
export PGPASSWORD='Nokia#5300'
psql -h researchanalyst-db.cle6mqs82txq.ap-south-1.rds.amazonaws.com \
     -U postgres -d researchanalyst -p 5432 \
     -c "\dt"
unset PGPASSWORD
```

### Test S3
```bash
aws s3 ls s3://researchanalyst-storage/ --recursive
```

### Test All Connections
```bash
./test_connections.sh
```

---

## 🔐 Security Checklist

### Production Security (Do Before Launch)

- [ ] Change database password from default
- [ ] Restrict RDS security group to specific IPs (remove 0.0.0.0/0)
- [ ] Enable RDS SSL/TLS connections
- [ ] Update S3 CORS to specific frontend domain
- [ ] Enable S3 access logging
- [ ] Use VPC endpoints for OpenSearch
- [ ] Enable CloudWatch alarms
- [ ] Set up AWS Secrets Manager for credentials
- [ ] Enable AWS CloudTrail for audit logging

---

## 💰 Cost Estimate

### Free Tier (First 12 months)
- RDS db.t3.micro: **$0** (750 hrs/month)
- S3 storage (5GB): **$0**
- OpenSearch t3.small: **$0** (750 hrs/month)
- **Total: $0-10/month**

### After Free Tier
- RDS db.t3.medium: **~$60/month**
- S3 (100GB + requests): **~$5/month**
- OpenSearch t3.small (HA x3): **~$150/month**
- Data transfer: **~$10/month**
- **Total: ~$225-250/month**

---

## 📚 Documentation Reference

- **Quick Start:** `CLOUDSHELL_QUICKSTART.md`
- **Full Guide:** `AWS_SETUP_GUIDE.md`
- **API Spec:** `api_documentation.md`
- **Architecture:** `architecture_1.md`
- **PRD:** `PRD.md`

---

## 🆘 Troubleshooting

### Connection Timeout
```bash
# Fix RDS security group
aws ec2 describe-security-groups --filters "Name=group-name,Values=*researchanalyst*"

# Add your IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp --port 5432 \
  --cidr $(curl -s https://checkip.amazonaws.com)/32
```

### Permission Denied
```bash
# Check AWS identity
aws sts get-caller-identity

# Ensure IAM user has these policies:
# - AmazonRDSFullAccess
# - AmazonS3FullAccess
# - AmazonOpenSearchServiceFullAccess
```

### Migration Failed
```bash
# Check existing tables
psql -h YOUR_ENDPOINT -U postgres -d researchanalyst -c "\dt"

# Drop and recreate (CAUTION: deletes all data)
psql -h YOUR_ENDPOINT -U postgres -d researchanalyst \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migration
psql -h YOUR_ENDPOINT -U postgres -d researchanalyst -f db_migration.sql
```

---

## 🎓 Next Steps

1. ✅ **Complete infrastructure setup** (you're here)
2. ⏭️ **Create OpenSearch domain** (10 min)
3. ⏭️ **Setup Cognito User Pool** (5 min)
4. ⏭️ **Deploy Lambda backend** (handlers from PRD)
5. ⏭️ **Configure API Gateway** (route endpoints)
6. ⏭️ **Test API endpoints** (Postman/curl)
7. ⏭️ **Build frontend** (React/Next.js)
8. ⏭️ **Deploy to production**

---

## 📞 Resources

- **AWS RDS Console:** https://ap-south-1.console.aws.amazon.com/rds/
- **AWS S3 Console:** https://s3.console.aws.amazon.com/s3/buckets/researchanalyst-storage
- **OpenSearch Console:** https://ap-south-1.console.aws.amazon.com/aos/
- **CloudShell:** Click (>_) icon in AWS Console top bar

---

## ✨ You're Ready!

All infrastructure setup files are ready. Just upload to CloudShell and run `setup_all.sh`!

**Questions?** Check `CLOUDSHELL_QUICKSTART.md` or `AWS_SETUP_GUIDE.md` for detailed steps.


