# ResearchAnalyst API – Backend ↔ Frontend Contract

## 0. High-level

* **Auth**: Amazon Cognito (ID/Access token in `Authorization: Bearer <JWT>`)
* **Gateway**: Amazon API Gateway (HTTP API)
* **Compute**: AWS Lambda (Python or Java)
* **Data**: RDS Postgres, OpenSearch, S3

Base URL (example):

```text
https://api.researchanalyst.io/v1
```

All endpoints below are **prefixed with `/v1`**.

---

## 1. Conventions

### 1.1 Authentication

All protected endpoints require:

```http
Authorization: Bearer <JWT_FROM_COGNITO>
```

Backend will:

* Validate JWT against Cognito.
* Resolve or create `users` row.
* Attach `user.id` to the request context.

---

### 1.2 Common response format

**Success**: domain-specific JSON body.

**Error JSON format** (always):

```json
{
  "error_code": "STRING_CODE",
  "message": "Human readable error",
  "details": { "field": "optional extra info" }
}
```

Common error codes:

* `UNAUTHENTICATED`
* `FORBIDDEN`
* `VALIDATION_ERROR`
* `NOT_FOUND`
* `CONFLICT`
* `INTERNAL_ERROR`
* `UPSTREAM_ERROR` (e.g., TijoriStack issues)

---

### 1.3 Pagination

Pattern:

```http
GET /v1/... ?page=1&page_size=20
```

Response includes:

```json
{
  "items": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 123,
    "total_pages": 7
  }
}
```

---

## 2. Auth & User Profile

> Login itself handled by Cognito Hosted UI – backend **does not** expose `/login`.

### 2.1 `GET /v1/auth/me`

**Description:** Returns current user’s profile, plan, and basic usage summary.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "id": "7f4c6f1e-1e50-4f74-90ca-8a1a72c1b1a1",
  "email": "user@example.com",
  "plan_tier": "trial",
  "created_at": "2025-12-04T10:00:00Z",
  "usage": {
    "period": "2025-12",
    "transcripts_used": 12,
    "transcripts_quota": 600,
    "tokens_used": 120000,
    "tokens_quota": 1000000
  }
}
```

---

## 3. Companies & Search

### 3.1 `GET /v1/companies/search`

**Description:** Search stocks by name, ticker, or ISIN (backed by OpenSearch). Used for autocomplete and company selection.

* **Auth:** Required
* **Method:** `GET`
* **Query params:**

  * `q` (string, required) – search text
  * `limit` (int, optional, default: 10)

**Example:**

```http
GET /v1/companies/search?q=tcs&limit=5
```

**Response 200:**

```json
{
  "items": [
    {
      "id": 123,
      "isin": "INE123A01016",
      "display_name": "Tata Consultancy Services Ltd",
      "ticker": "TCS",
      "exchange": "NSE",
      "sector_name": "IT Services"
    }
  ]
}
```

---

### 3.2 `GET /v1/companies/{company_id}`

**Description:** Get canonical company detail by internal `company_id`.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "id": 123,
  "isin": "INE123A01016",
  "display_name": "Tata Consultancy Services Ltd",
  "ticker": "TCS",
  "exchange": "NSE",
  "sector_name": "IT Services",
  "slug": "tcs"
}
```

---

### 3.3 `GET /v1/companies/by-isin/{isin}`

**Description:** Fetch company by ISIN, creating it (and seeding from Tijori) if necessary.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

Same as `/companies/{company_id}`.

---

## 4. Concall & Transcript Layer

### 4.1 `GET /v1/companies/{company_id}/concalls/latest`

**Description:** Return latest completed concall for a company.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "concall_id": 987,
  "status": "COMPLETED",
  "concall_event_time": "2025-11-01T09:00:00Z",
  "recording_link": "https://...",
  "has_transcript": true,
  "transcript_file_id": "c6717a94-...",
  "analysis_file_id": "2f1039e7-...",
  "last_analysis_updated_at": "2025-11-01T09:30:00Z"
}
```

---

### 4.2 `GET /v1/companies/{company_id}/concalls`

**Description:** Paginated list of concalls (past + upcoming).

* **Auth:** Required
* **Method:** `GET`
* **Query params:**

  * `status` (optional): `UPCOMING` / `COMPLETED` / `ALL`
  * `page`, `page_size`

**Response 200:**

```json
{
  "items": [
    {
      "concall_id": 987,
      "status": "COMPLETED",
      "concall_event_time": "2025-11-01T09:00:00Z",
      "recording_link": "https://...",
      "has_transcript": true
    }
  ],
  "pagination": { ... }
}
```

---

### 4.3 `GET /v1/concalls/{concall_id}/transcript`

**Description:** Returns transcript metadata + S3 download URL (pre-signed URL).

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "concall_id": 987,
  "transcript_file_id": "c6717a94-...",
  "download_url": "https://researchanalyst-storage.s3...&X-Amz-SignedHeaders=host",
  "expires_at": "2025-12-06T11:00:00Z"
}
```

---

## 5. Watchlists

### 5.1 `GET /v1/watchlists`

**Description:** Get all watchlists for current user.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "items": [
    {
      "id": "b7e2f6c3-...",
      "name": "My IT Picks",
      "type": "NORMAL",
      "description": null,
      "created_at": "2025-12-01T10:00:00Z",
      "updated_at": "2025-12-01T11:00:00Z"
    },
    {
      "id": "aa0f2f6c-...",
      "name": "Auto OEM Sector",
      "type": "SECTOR",
      "description": "All major auto OEMs",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

### 5.2 `POST /v1/watchlists`

**Description:** Create new watchlist (normal or sector).

* **Auth:** Required
* **Method:** `POST`

**Request body:**

```json
{
  "name": "My IT Picks",
  "type": "NORMAL",
  "description": "My personal IT stocks"
}
```

**Response 201:**

```json
{
  "id": "b7e2f6c3-...",
  "name": "My IT Picks",
  "type": "NORMAL",
  "description": "My personal IT stocks",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T10:00:00Z"
}
```

---

### 5.3 `GET /v1/watchlists/{watchlist_id}`

**Description:** Get watchlist detail including items.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "id": "b7e2f6c3-...",
  "name": "My IT Picks",
  "type": "NORMAL",
  "description": "My personal IT stocks",
  "items": [
    {
      "id": "item-uuid-1",
      "company_id": 123,
      "stock_name": "Tata Consultancy Services Ltd",
      "stock_isin": "INE123A01016",
      "position_order": 1,
      "last_analysis_file_id": "2f1039e7-...",
      "last_analysis_updated_at": "2025-11-01T09:30:00Z"
    }
  ],
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T11:00:00Z"
}
```

---

### 5.4 `PATCH /v1/watchlists/{watchlist_id}`

**Description:** Update name, type, description.

* **Auth:** Required
* **Method:** `PATCH`

**Request body (any subset):**

```json
{
  "name": "Updated Name",
  "description": "New description"
}
```

**Response 200:** Updated watchlist object.

---

### 5.5 `DELETE /v1/watchlists/{watchlist_id}`

**Description:** Delete watchlist and its items.

* **Auth:** Required
* **Method:** `DELETE`

**Response 204:** No body.

---

### 5.6 `POST /v1/watchlists/{watchlist_id}/items`

**Description:** Add stock to a watchlist.

* **Auth:** Required
* **Method:** `POST`

**Request body:**

```json
{
  "company_id": 123
}
```

or (if you want to allow direct ISIN):

```json
{
  "isin": "INE123A01016"
}
```

Backend will:

* Resolve `company_id` (creating `companies` row if needed).
* Create `watchlist_items` row.

**Response 201:**

```json
{
  "id": "item-uuid-1",
  "company_id": 123,
  "stock_name": "Tata Consultancy Services Ltd",
  "stock_isin": "INE123A01016",
  "position_order": 3,
  "last_analysis_file_id": null,
  "last_analysis_updated_at": null
}
```

---

### 5.7 `DELETE /v1/watchlists/{watchlist_id}/items/{item_id}`

**Description:** Remove stock from watchlist.

* **Auth:** Required
* **Method:** `DELETE`

**Response 204.**

---

## 6. Analysis Endpoints

### 6.1 `POST /v1/companies/{company_id}/analysis`

**Description:** Trigger or re-trigger analysis for the **latest concall** of a company.

* **Auth:** Required
* **Method:** `POST`

**Request body (optional):**

```json
{
  "force_rerun": false
}
```

Backend logic:

* Find latest completed concall (via Tijori or DB cache).
* Ensure transcript exists (download + ASR if needed).
* Run LLM analysis (Gemini, etc.).
* Store result in S3 & `files` / `analyses`.
* Update `watchlist_items.last_analysis_file_id` where relevant.

**Response 202:**

```json
{
  "status": "QUEUED",
  "company_id": 123,
  "concall_id": 987,
  "analysis_file_id": null
}
```

or if synchronous (for v1 small load):

**Response 200:**

```json
{
  "status": "COMPLETED",
  "analysis_file_id": "2f1039e7-...",
  "summary": {
    "headline": "Strong QoQ growth, margin stable",
    "key_points": [ "...", "..." ]
  }
}
```

---

### 6.2 `GET /v1/companies/{company_id}/analysis/latest`

**Description:** Get latest analysis for a company.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "company_id": 123,
  "concall_id": 987,
  "analysis_file_id": "2f1039e7-...",
  "created_at": "2025-11-01T09:30:00Z",
  "model": "gemini-3-pro-preview",
  "summary": {
    "headline": "Strong QoQ growth, margin stable",
    "key_points": [ "...", "..." ],
    "risks": [ "..." ],
    "management_tone": "neutral-to-positive"
  }
}
```

---

### 6.3 `POST /v1/watchlists/{watchlist_id}/analysis`

**Description:** Sector-level / basket-level analysis (e.g., “compare all stocks in this watchlist”).

* **Auth:** Required
* **Method:** `POST`

**Request body (optional):**

```json
{
  "force_rerun": false
}
```

**Response 202 (or 200 if synchronous):**

```json
{
  "status": "QUEUED",
  "watchlist_id": "b7e2f6c3-..."
}
```

---

## 7. Exports

### 7.1 `POST /v1/watchlists/{watchlist_id}/export`

**Description:** Generate export (e.g., Excel/PDF) for a watchlist’s current analysis state.

* **Auth:** Required
* **Method:** `POST`

**Response 202:**

```json
{
  "status": "QUEUED",
  "export_id": "export-uuid-1"
}
```

### 7.2 `GET /v1/exports/{export_id}`

**Description:** Get export status + download URL.

* **Auth:** Required
* **Method:** `GET`

**Response 200:**

```json
{
  "status": "COMPLETED",
  "export_id": "export-uuid-1",
  "download_url": "https://researchanalyst-storage.s3...X-Amz-Signature=...",
  "expires_at": "2025-12-06T11:00:00Z"
}
```

---
