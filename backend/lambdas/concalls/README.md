# Conference Calls Lambda Functions

## Endpoints:

### GET /v1/companies/{company_id}/concalls/latest
Get latest completed concall for a company

**Status:** 🔴 Not implemented yet

**Integration:** TijoriStack API

---

### GET /v1/companies/{company_id}/concalls
List all concalls (paginated)

**Status:** 🔴 Not implemented yet

---

### GET /v1/concalls/{concall_id}/transcript
Get transcript download URL (S3 pre-signed)

**Status:** 🔴 Not implemented yet

**Requirements:** S3 integration

---

## Database Tables:
- `concalls` - Conference call metadata
- `files` - Transcript/audio file references

