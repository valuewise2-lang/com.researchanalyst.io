# Analysis Lambda Functions

## Endpoints:

### POST /v1/companies/{company_id}/analysis
Trigger LLM analysis for latest concall

**Status:** ✅ Partially implemented in `lambda_handler.py`

**Handler:** `lambda_handler`

**Current:** Works with company name, downloads transcripts, runs Gemini analysis

**TODO:** 
- Add Cognito authentication
- Store results in S3
- Update `files` table
- Link to `watchlist_items.last_analysis_file_id`

---

### GET /v1/companies/{company_id}/analysis/latest
Get latest analysis for a company

**Status:** 🔴 Not implemented yet

**Requirements:** S3 integration for reading analysis files

---

### POST /v1/watchlists/{watchlist_id}/analysis
Sector-level analysis (compare all companies)

**Status:** 🔴 Not implemented yet

---

## Current Implementation:

`lambda_handler.py` includes:
- ISIN lookup from Equity.csv
- TijoriStack transcript download
- Gemini LLM analysis
- PDF parsing

**Next steps:** Add auth, S3 storage, database tracking

