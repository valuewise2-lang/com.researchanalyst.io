# Watchlists Lambda Functions

## Endpoints:

### POST /v1/watchlists
Create a new watchlist for a user

**Status:** ✅ Implemented in `lambda_watchlists.py`

**Handler:** `create_watchlist`

---

### GET /v1/watchlists?user_id=xxx
Get all watchlists for a user

**Status:** ✅ Implemented in `lambda_watchlists.py`

**Handler:** `get_watchlists`

---

### GET /v1/watchlists/{watchlist_id}
Get specific watchlist with items

**Status:** ✅ Implemented in `lambda_watchlists.py`

**Handler:** `get_watchlist_by_id`

---

### POST /v1/watchlists/{watchlist_id}/items
Add company to watchlist

**Status:** ✅ Implemented in `lambda_watchlists.py`

**Handler:** `add_company_to_watchlist`

---

### DELETE /v1/watchlists/{watchlist_id}
Delete watchlist

**Status:** 🔴 Not implemented yet

---

### DELETE /v1/watchlists/{watchlist_id}/items/{item_id}
Remove company from watchlist

**Status:** 🔴 Not implemented yet

---

## Testing:

```bash
python3 lambda_watchlists.py
```

