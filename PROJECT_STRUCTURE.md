# ResearchAnalyst - Complete Project Structure

**Clean, organized, production-ready structure** ✅

---

## 📁 Directory Organization

```
learning/
│
├── 📂 backend/                           # All backend code
│   │
│   ├── 📂 lambdas/                       # AWS Lambda functions (one folder per API)
│   │   │
│   │   ├── 📂 auth/                      # Authentication API
│   │   │   └── README.md                 # Status: 🔴 Empty (future)
│   │   │
│   │   ├── 📂 watchlists/                # Watchlist Management API
│   │   │   ├── README.md                 # API documentation
│   │   │   └── lambda_watchlists.py      # ✅ IMPLEMENTED
│   │   │       → POST /v1/watchlists     # Create watchlist
│   │   │       → GET /v1/watchlists      # List watchlists
│   │   │       → GET /v1/watchlists/{id} # Get details
│   │   │       → POST /v1/watchlists/{id}/items # Add company
│   │   │
│   │   ├── 📂 companies/                 # Companies API
│   │   │   └── README.md                 # Status: 🔴 Empty (future)
│   │   │
│   │   ├── 📂 concalls/                  # Conference Calls API
│   │   │   └── README.md                 # Status: 🔴 Empty (future)
│   │   │
│   │   └── 📂 analysis/                  # LLM Analysis API
│   │       ├── README.md                 # API documentation
│   │       └── lambda_handler.py         # ⚠️ PARTIAL
│   │           → POST /v1/analyze        # Company analysis
│   │
│   └── 📂 lib/                           # Shared libraries (reusable code)
│       ├── README.md                     # Library documentation
│       └── cognito_auth.py               # ✅ COMPLETE
│           → authenticate_request()      # Main auth function
│           → verify_jwt_token()          # JWT verification
│           → get_or_create_user()        # User sync (lazy creation)
│
├── 📂 database/                          # Database schema & data
│   │
│   ├── 📂 schema/                        # Table definitions
│   │   └── db_migration.sql              # ✅ Complete schema (6 tables)
│   │       → users, companies, watchlists, watchlist_items
│   │       → concalls, files
│   │       → All indexes, constraints, triggers
│   │
│   ├── 📂 scripts/                       # Data import scripts
│   │   └── companies_insert.sql          # ✅ 4,729 BSE companies
│   │       → INSERT statements for all companies
│   │
│   └── 📂 docs/                          # Architecture documentation
│       ├── PRD.md                        # Product Requirements Document
│       ├── architecture_1.md             # Database design & ERD
│       ├── api_documentation.md          # API contracts & specs
│       └── tijori-api-docs.md            # TijoriStack API reference
│
├── 📂 aws-deployment/                    # AWS infrastructure setup
│   │
│   ├── 📂 guides/                        # Step-by-step guides
│   │   ├── AWS_SETUP_GUIDE.md            # Complete AWS setup (RDS, S3, OpenSearch)
│   │   ├── OPENSEARCH_SETUP_GUIDE.md     # OpenSearch detailed guide (on hold)
│   │   └── SETUP_SUMMARY.md              # Quick reference
│   │
│   ├── 📂 scripts/                       # Automation scripts
│   │   ├── cloudshell_setup.sh           # RDS setup via CloudShell
│   │   ├── cloudshell_setup_s3.sh        # S3 setup via CloudShell
│   │   ├── s3_setup.py                   # S3 Python automation
│   │   └── opensearch_setup.py           # OpenSearch automation
│   │
│   └── 📂 config/                        # Configuration files
│       ├── opensearch_mapping.json       # OpenSearch index mapping
│       └── requirements_aws.txt          # Python dependencies for AWS scripts
│
├── 📂 Tijori/                            # (pre-existing folder - untouched)
│
├── 📄 Equity.csv                         # ✅ Source data: 4,731 BSE companies
├── 📄 README.md                          # ✅ Main project documentation
└── 📄 PROJECT_STRUCTURE.md               # ✅ This file
```

---

## ✅ Files Cleaned Up (Deleted)

**Removed from root:**
- ✅ `example_usage.py` - Example code
- ✅ `promptchain.py` - Test script
- ✅ `tijori_llm_analysis.py` - Old version (refactored into Lambda)
- ✅ `test_tijori_tools.py` - Old test
- ✅ `requirements_tijori.txt` - Old requirements
- ✅ `my_program` - Unrelated binary
- ✅ `Dockerfile` - Not needed yet
- ✅ Duplicate Lambda files (moved to organized folders)

---

## 📊 What's Implemented vs TODO

### ✅ **COMPLETE:**
1. **Database Schema** - 6 tables, all relationships, indexes
2. **Companies Data** - 4,729 BSE companies imported
3. **Cognito Setup** - User pool, app client configured
4. **Auth Library** - JWT verification + lazy user creation
5. **Watchlists API** - 4 endpoints fully working

### ⚠️ **PARTIAL:**
1. **Analysis API** - Works but needs auth integration

### 🔴 **TODO:**
1. **S3 Bucket** - Setup scripts ready
2. **Companies API** - Search, get by ISIN
3. **Concalls API** - List, get latest
4. **Auth API** - GET /me endpoint
5. **OpenSearch** - On hold (cost reasons)

---

## 🎯 Your Clean Root Directory

Now your root only contains:
```
learning/
├── backend/          # All code
├── database/         # All DB stuff
├── aws-deployment/   # All AWS stuff
├── Tijori/           # Pre-existing
├── Equity.csv        # Source data
└── README.md         # Main docs
```

**Clean, professional, organized!** 🎉

---

## 🚀 Next Steps

1. **Test locally:** 
   ```bash
   python3 backend/lambdas/watchlists/lambda_watchlists.py
   ```

2. **Deploy to AWS Lambda**

3. **Set up API Gateway**

4. **Build frontend** at https://researchanalyst.io

---

**Everything is now organized exactly as you requested!** Each API has its own folder, database files are separate, and AWS deployment guides are in their own section. 🎨✨
