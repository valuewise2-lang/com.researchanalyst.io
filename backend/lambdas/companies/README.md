# Companies Lambda Functions

## Endpoints:

### GET /v1/companies/search?q=TEXT
Search companies by name, ticker, or ISIN

**Status:** 🔴 Not implemented yet

**Requirements:** OpenSearch integration

---

### GET /v1/companies/{company_id}
Get company details by ID

**Status:** 🔴 Not implemented yet

---

### GET /v1/companies/by-isin/{isin}
Get company by ISIN (create from Tijori if not exists)

**Status:** 🔴 Not implemented yet

---

## Database:
Uses `companies` table (4,729 BSE companies already loaded)

