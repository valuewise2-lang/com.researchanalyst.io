# Shared Library Functions

Reusable modules imported by all Lambda functions.

## Files:

### cognito_auth.py ✅
**Purpose:** JWT verification and user authentication

**Functions:**
- `authenticate_request(auth_header)` - Main auth function
- `verify_jwt_token(token)` - Verify JWT signature
- `get_or_create_user(claims)` - Sync user to database (lazy creation)
- `get_jwks()` - Fetch Cognito public keys

**Used by:** All protected Lambda functions

---

### db.py 🔴
**Purpose:** Database connection pooling and helpers

**TODO:** Create shared database utilities

---

### s3.py 🔴
**Purpose:** S3 operations (upload, download, pre-signed URLs)

**TODO:** Create S3 helper functions

---

### tijori.py 🔴
**Purpose:** TijoriStack API integration

**TODO:** Extract Tijori functions from lambda_handler.py

---

### llm.py 🔴
**Purpose:** LLM (Gemini/OpenAI) integration

**TODO:** Extract LLM functions from lambda_handler.py

---

## Usage in Lambda:

```python
# In any Lambda function:
import sys
sys.path.append('/opt/python')  # Lambda layer path

from lib.cognito_auth import authenticate_request
from lib.db import get_connection
from lib.s3 import upload_file, generate_presigned_url

def lambda_handler(event, context):
    user = authenticate_request(event['headers']['Authorization'])
    # ... your logic
```

