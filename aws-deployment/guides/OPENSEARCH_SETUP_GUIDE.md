# OpenSearch Setup Guide - Step by Step

Complete guide to creating OpenSearch domain and populating with BSE company data.

---

## Part 1: Create OpenSearch Domain (AWS Console)

### Step 1: Open OpenSearch Service

1. Go to AWS Console: https://console.aws.amazon.com/
2. Search for **"OpenSearch"** in the top search bar
3. Click **"Amazon OpenSearch Service"**
4. Make sure you're in region: **ap-south-1** (Mumbai)

### Step 2: Create Domain

Click the **"Create domain"** button

### Step 3: Configure Domain

#### General Settings:
- **Domain name:** `researchanalyst-search`
- **Domain creation method:** Standard create
- **Templates:** Dev/test

#### Deployment:
- **Deployment option(s):** Domain with standby
- **Availability Zone(s):** 1-AZ (cheaper for dev)
- **Engine options:**
  - **OpenSearch version:** 2.11 or latest
  - **Auto-Tune:** Enabled

#### Data Nodes:
- **Instance type:** `t3.small.search` (2 vCPU, 2 GiB RAM)
  - ✅ Free tier eligible (750 hours/month for first year)
- **Number of nodes:** 1
- **Warm and cold data storage:** Disabled

#### Storage:
- **EBS storage size per node:** 10 GB
- **EBS volume type:** GP3 (General Purpose SSD)

#### Network:
- **Network:** Public access
  - (For production, use VPC access)
- **Enable custom endpoint:** No

#### Fine-grained Access Control:
- **Enable fine-grained access control:** ✅ **YES** (Check this!)
- **Create master user:** ✅ **YES**
- **Master username:** `admin`
- **Master password:** Choose a strong password
  - Example: `Admin@12345`
  - **SAVE THIS PASSWORD!** You'll need it later

#### Access Policy:
- **Domain access policy:** Only use fine-grained access control
- **Do NOT configure additional access policy** (fine-grained control is enough)

#### Encryption:
- **Encryption at rest:** Enabled (default)
- **Node-to-node encryption:** Enabled (default)

#### Tags (Optional):
- Add tag: `Project` = `ResearchAnalyst`

### Step 4: Review and Create

1. **Review all settings**
2. **Click "Create"**
3. **Wait 10-15 minutes** for domain to become active

---

## Part 2: Get OpenSearch Endpoint

### Once Domain is Active:

1. Go to **OpenSearch → Domains → researchanalyst-search**
2. Copy the **Endpoint** (under General information)
   - Example: `search-researchanalyst-search-abc123xyz.ap-south-1.es.amazonaws.com`
3. **SAVE THIS ENDPOINT!**

---

## Part 3: Update and Run Python Script

### Step 1: Install Required Packages

```bash
cd /Users/avadhech/Documents/learning
pip3 install opensearch-py requests-aws4auth boto3 --break-system-packages
```

### Step 2: Update Configuration

Open `populate_opensearch.py` and update these lines:

```python
OPENSEARCH_ENDPOINT = "search-researchanalyst-search-YOUR-ENDPOINT.ap-south-1.es.amazonaws.com"
MASTER_USERNAME = "admin"
MASTER_PASSWORD = "YOUR_PASSWORD_HERE"  # The password you set when creating domain
```

### Step 3: Run the Script

```bash
python3 populate_opensearch.py
```

This will:
- ✅ Connect to OpenSearch
- ✅ Create `companies_v1` index with proper mappings
- ✅ Import all 4,729 companies from `Equity.csv`
- ✅ Test search functionality

---

## Part 4: Verify OpenSearch is Working

### Test 1: Using cURL

```bash
# Replace with your endpoint and password
ENDPOINT="search-researchanalyst-search-xyz.ap-south-1.es.amazonaws.com"
PASSWORD="your_password"

# Test connection
curl -X GET "https://${ENDPOINT}/_cluster/health?pretty" \
  -u "admin:${PASSWORD}"

# Count documents
curl -X GET "https://${ENDPOINT}/companies_v1/_count?pretty" \
  -u "admin:${PASSWORD}"

# Search for TCS
curl -X POST "https://${ENDPOINT}/companies_v1/_search?pretty" \
  -u "admin:${PASSWORD}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "multi_match": {
        "query": "tcs",
        "fields": ["display_name^3", "ticker^2", "aliases^2"]
      }
    },
    "size": 5
  }'
```

### Test 2: Using Python

```python
from opensearchpy import OpenSearch, RequestsHttpConnection

client = OpenSearch(
    hosts=[{'host': 'YOUR_ENDPOINT', 'port': 443}],
    http_auth=('admin', 'YOUR_PASSWORD'),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Search
response = client.search(
    index='companies_v1',
    body={
        "query": {
            "multi_match": {
                "query": "reliance",
                "fields": ["display_name^3", "ticker^2"]
            }
        },
        "size": 10
    }
)

for hit in response['hits']['hits']:
    print(f"{hit['_source']['display_name']} - {hit['_source']['ticker']}")
```

---

## Part 5: OpenSearch Dashboards (Visual Interface)

### Access Dashboards:

1. Go to your OpenSearch domain in AWS Console
2. Click **"OpenSearch Dashboards URL"**
   - Example: `https://search-researchanalyst-search-xyz.ap-south-1.es.amazonaws.com/_dashboards`
3. **Login with:**
   - Username: `admin`
   - Password: Your master password

### Explore Your Data:

1. **Go to Dev Tools** (left sidebar)
2. **Run queries:**

```json
GET companies_v1/_search
{
  "query": {
    "match": {
      "display_name": "tata"
    }
  }
}

GET companies_v1/_count

GET companies_v1/_mapping
```

---

## Troubleshooting

### Error: "Connection timeout"

**Solution:** Update access policy to allow your IP

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:ap-south-1:ACCOUNT_ID:domain/researchanalyst-search/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["YOUR_IP/32"]
        }
      }
    }
  ]
}
```

### Error: "Authentication failed"

- Check username is `admin`
- Check password is correct
- Try resetting master user password in AWS Console

### Error: "Index already exists"

- Script will ask if you want to delete and recreate
- Or manually delete: 
  ```bash
  curl -X DELETE "https://ENDPOINT/companies_v1" -u "admin:password"
  ```

---

## Cost Information

### Free Tier (First 12 months):
- **t3.small.search:** 750 hours/month = $0
- **10 GB storage:** Included = $0
- **Total:** $0/month

### After Free Tier:
- **t3.small.search:** ~$0.048/hour = ~$35/month
- **10 GB GP3 storage:** ~$1/month
- **Data transfer:** ~$1/month
- **Total:** ~$37/month (single node)

### Production (3 nodes for HA):
- ~$110/month

---

## Quick Reference

| Setting | Value |
|---------|-------|
| **Domain** | researchanalyst-search |
| **Region** | ap-south-1 |
| **Index** | companies_v1 |
| **Username** | admin |
| **Instance** | t3.small.search |
| **Storage** | 10 GB GP3 |
| **Documents** | 4,729 companies |

---

## Summary Checklist

- [ ] OpenSearch domain created
- [ ] Domain status is "Active" (green)
- [ ] Endpoint copied and saved
- [ ] Master user credentials saved
- [ ] Python packages installed
- [ ] `populate_opensearch.py` configured
- [ ] Script executed successfully
- [ ] Index contains 4,729 documents
- [ ] Search functionality tested
- [ ] OpenSearch Dashboards accessible

---

**You're all set!** Your companies are now searchable via OpenSearch! 🎉

