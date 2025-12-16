# ResearchAnalyst Backend

Complete backend infrastructure for ResearchAnalyst - AI-powered Indian stock market analysis platform.

---

## 📁 Project Structure

```
learning/
│
├── backend/                          # Backend Lambda functions and libraries
│   ├── lambdas/                      # AWS Lambda handlers
│   │   ├── auth/                     # Authentication endpoints
│   │   │   ├── README.md             # Auth API documentation
│   │   │   └── (empty - TODO)
│   │   │
│   │   ├── watchlists/               # Watchlist management
│   │   │   ├── README.md             # Watchlist API documentation
│   │   │   └── lambda_watchlists.py  # ✅ Implemented
│   │   │       • POST /v1/watchlists
│   │   │       • GET /v1/watchlists
│   │   │       • GET /v1/watchlists/{id}
│   │   │       • POST /v1/watchlists/{id}/items
│   │   │
│   │   ├── companies/                # Company search & details
│   │   │   ├── README.md             # Companies API documentation
│   │   │   └── (empty - TODO)
│   │   │
│   │   ├── concalls/                 # Conference calls & transcripts
│   │   │   ├── README.md             # Concalls API documentation
│   │   │   └── (empty - TODO)
│   │   │
│   │   └── analysis/                 # LLM analysis
│   │       ├── README.md             # Analysis API documentation
│   │       └── lambda_handler.py     # ✅ Implemented (partial)
│   │           • POST /v1/analyze (company analysis)
│   │
│   └── lib/                          # Shared libraries
│       ├── README.md                 # Library documentation
│       └── cognito_auth.py           # ✅ JWT verification & user sync
│
├── database/                         # Database schema and scripts
│   ├── schema/                       # Table definitions
│   │   └── db_migration.sql          # ✅ 6 tables with indexes
│   │
│   ├── scripts/                      # Population scripts
│   │   └── companies_insert.sql      # ✅ 4,729 BSE companies
│   │
│   └── docs/                         # Architecture documentation
│       ├── PRD.md                    # Product Requirements
│       ├── architecture_1.md         # Database design
│       └── api_documentation.md      # API contracts
│
├── aws-deployment/                   # AWS infrastructure setup
│   ├── guides/                       # Step-by-step guides
│   │   ├── AWS_SETUP_GUIDE.md        # Complete AWS setup
│   │   ├── OPENSEARCH_SETUP_GUIDE.md # OpenSearch (on hold)
│   │   ├── COGNITO_NEXT_STEPS.md     # Cognito integration
│   │   └── SETUP_SUMMARY.md          # Quick summary
│   │
│   ├── scripts/                      # Automation scripts
│   │   ├── cloudshell_setup.sh       # Database setup (CloudShell)
│   │   ├── cloudshell_setup_s3.sh    # S3 setup
│   │   ├── s3_setup.py               # S3 Python setup
│   │   ├── opensearch_setup.py       # OpenSearch setup
│   │   └── populate_opensearch.py    # OpenSearch data import
│   │
│   └── config/                       # Configuration files
│       ├── opensearch_mapping.json   # OpenSearch index mapping
│       └── requirements_aws.txt      # Python dependencies
│
├── Equity.csv                        # BSE company data (4,731 rows)
├── lambda_handler.py                 # Original analysis Lambda (root)
├── lambda_watchlists.py              # Original watchlists Lambda (root)
├── cognito_auth.py                   # Original auth lib (root)
└── README.md                         # This file
```

---

## 🗄️ Database Status

### PostgreSQL RDS:
- **Endpoint:** `researchanalyst-db.cle6mqs82txq.ap-south-1.rds.amazonaws.com:5432`
- **Database:** `postgres`
- **Status:** ✅ Active

### Tables Created (6):
1. ✅ **users** - User accounts (1 test user)
2. ✅ **companies** - BSE companies (4,729 records)
3. ✅ **watchlists** - User watchlists (1 test watchlist)
4. ✅ **watchlist_items** - Companies in watchlists (0 items)
5. ✅ **concalls** - Conference call events (0 records)
6. ✅ **files** - S3 file references (0 records)

---

## 🔐 Authentication Status

### Cognito User Pool:
- **Pool ID:** `ap-south-1_1lUBZPVma`
- **App Client ID:** `4odpufu4q9mp1lltmpuus1iqa7`
- **Domain:** `ap-south-11lubzpvma.auth.ap-south-1.amazoncognito.com`
- **Status:** ✅ Configured

### Authentication Library:
- ✅ JWT verification implemented (`cognito_auth.py`)
- ✅ Lazy user creation (on first API call)
- ✅ Ready to use in all Lambda functions

---

## 📡 API Implementation Status

| Endpoint | Method | Status | File | Handler |
|----------|--------|--------|------|---------|
| **Auth** |
| `/v1/auth/me` | GET | 🔴 TODO | - | - |
| **Companies** |
| `/v1/companies/search` | GET | 🔴 TODO | - | - |
| `/v1/companies/{id}` | GET | 🔴 TODO | - | - |
| `/v1/companies/by-isin/{isin}` | GET | 🔴 TODO | - | - |
| **Watchlists** |
| `/v1/watchlists` | POST | ✅ Done | `watchlists/lambda_watchlists.py` | `create_watchlist` |
| `/v1/watchlists` | GET | ✅ Done | `watchlists/lambda_watchlists.py` | `get_watchlists` |
| `/v1/watchlists/{id}` | GET | ✅ Done | `watchlists/lambda_watchlists.py` | `get_watchlist_by_id` |
| `/v1/watchlists/{id}/items` | POST | ✅ Done | `watchlists/lambda_watchlists.py` | `add_company_to_watchlist` |
| `/v1/watchlists/{id}` | DELETE | 🔴 TODO | - | - |
| `/v1/watchlists/{id}/items/{item_id}` | DELETE | 🔴 TODO | - | - |
| **Concalls** |
| `/v1/companies/{id}/concalls/latest` | GET | 🔴 TODO | - | - |
| `/v1/concalls/{id}/transcript` | GET | 🔴 TODO | - | - |
| **Analysis** |
| `/v1/companies/{id}/analysis` | POST | ⚠️ Partial | `analysis/lambda_handler.py` | `lambda_handler` |
| `/v1/companies/{id}/analysis/latest` | GET | 🔴 TODO | - | - |

---

## 🚀 Quick Start

### 1. Database Setup (Already Done ✅)

```bash
# Tables created ✓
# Companies imported (4,729) ✓
```

### 2. Test Watchlists API Locally

```bash
cd /Users/avadhech/Documents/learning/backend/lambdas/watchlists
python3 lambda_watchlists.py
```

### 3. Deploy to AWS Lambda

```bash
# Package dependencies
pip install -t package/ psycopg2-binary

# Create deployment package
cd package && zip -r ../lambda_watchlists.zip . && cd ..
zip -g lambda_watchlists.zip lambda_watchlists.py
zip -g lambda_watchlists.zip ../../lib/cognito_auth.py

# Upload to AWS Lambda via Console or CLI
aws lambda create-function \
  --function-name watchlists-create \
  --runtime python3.11 \
  --handler lambda_watchlists.create_watchlist \
  --zip-file fileb://lambda_watchlists.zip \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role
```

---

## 🔧 Configuration

### Environment Variables Required:

```bash
# Cognito
COGNITO_REGION=ap-south-1
COGNITO_USER_POOL_ID=ap-south-1_1lUBZPVma
COGNITO_APP_CLIENT_ID=4odpufu4q9mp1lltmpuus1iqa7

# Database
DB_HOST=researchanalyst-db.cle6mqs82txq.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=Nokia#5300

# External APIs
TIJORISTACK_API_KEY=67358aa613024c2fa6e0e5156fe50421
TIJORISTACK_BASE_URL=https://www.tijoristack.ai/api/v1
GOOGLE_API_KEY=AIzaSyBfpwXVA0L6r4ex3HR6-kRiGXw0d8_94jM
GEMINI_MODEL=gemini-2.5-flash

# S3 (when ready)
S3_BUCKET=researchanalyst-storage
AWS_REGION=ap-south-1
```

---

## 📚 Documentation

### Database:
- **Schema:** `database/schema/db_migration.sql`
- **ERD:** `database/docs/architecture_1.md`
- **PRD:** `database/docs/PRD.md`

### APIs:
- **Contracts:** `database/docs/api_documentation.md`
- **Each Lambda:** See README.md in respective folder

### AWS Setup:
- **Complete Guide:** `aws-deployment/guides/AWS_SETUP_GUIDE.md`
- **Cognito:** `aws-deployment/guides/COGNITO_NEXT_STEPS.md`
- **OpenSearch:** `aws-deployment/guides/OPENSEARCH_SETUP_GUIDE.md` (on hold)

---

## 🎯 Next Steps

1. ✅ **Database** - Completed
2. ✅ **Companies Import** - Completed (4,729)
3. ✅ **Cognito Setup** - Completed
4. ✅ **Watchlists API** - Completed
5. ⏭️ **S3 Bucket Setup** - TODO
6. ⏭️ **Companies API** - TODO (needs OpenSearch or fallback)
7. ⏭️ **Concalls API** - TODO (needs Tijori integration)
8. ⏭️ **Analysis API** - TODO (complete with auth + S3)
9. ⏭️ **API Gateway Setup** - TODO
10. ⏭️ **Deploy to AWS** - TODO

---

## 💡 Development Tips

### Testing Locally:
```bash
# Each Lambda can run standalone
python3 backend/lambdas/watchlists/lambda_watchlists.py
python3 backend/lambdas/analysis/lambda_handler.py
```

### Database Queries:
```sql
-- View all data
SELECT * FROM users;
SELECT * FROM watchlists;
SELECT * FROM companies LIMIT 10;
```

### Cognito Test Login:
```
https://ap-south-11lubzpvma.auth.ap-south-1.amazoncognito.com/login?response_type=token&client_id=4odpufu4q9mp1lltmpuus1iqa7&redirect_uri=http://localhost:3000/callback&scope=openid+email+profile
```

---

## 🆘 Troubleshooting

### Database Connection Issues:
- Check RDS security group allows your IP
- Verify credentials in environment variables

### Cognito Issues:
- Verify User Pool ID and Client ID
- Check JWKS URL is accessible
- Ensure token hasn't expired (3600s)

### Lambda Deployment:
- Include all dependencies in deployment package
- Set environment variables in Lambda configuration
- Ensure Lambda role has RDS and S3 permissions

---

## 📞 Resources

- **AWS Console:** https://console.aws.amazon.com/
- **RDS:** https://ap-south-1.console.aws.amazon.com/rds/
- **Cognito:** https://ap-south-1.console.aws.amazon.com/cognito/
- **Lambda:** https://ap-south-1.console.aws.amazon.com/lambda/

---

**Built with:** Python 3.11+ | PostgreSQL 15 | AWS Lambda | Cognito | RDS

**Domain:** https://researchanalyst.io

