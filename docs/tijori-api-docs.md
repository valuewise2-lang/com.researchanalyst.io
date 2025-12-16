Below is the **complete TijoriStack Concall API Documentation in clean Markdown (MD)** — 
---

# 📘 TijoriStack – Concall API Documentation (Integration Spec)

**Base URL:**

```
https://www.tijoristack.ai/api/v1
```

**Primary Endpoint:**

```
GET /concalls/list
```

**Auth:**

```
Authorization: Bearer <TIJORISTACK_API_TOKEN>
Accept: application/json
```

---

# 1. Overview

TijoriStack provides APIs to fetch **earnings concall data** including:

* Completed concalls
* Upcoming concalls
* Recording links
* Company metadata (name, sector, slug)

Our application uses TijoriStack as the **single source of truth** for concall discovery and metadata.

---

# 2. Authentication

Requests require authentication with your API token.
Use the header:

```http
Authorization: Bearer <TIJORISTACK_API_TOKEN>
```

Environment variable in backend:

```env
TIJORISTACK_API_TOKEN=xxxxx
```

---

# 3. Endpoint: GET `/concalls/list`

### ✔ Purpose

Fetches **past or upcoming concalls** for companies.
Supports filtering by ISIN, pagination, and concall type.

---

## 3.1 Request

### **HTTP Method**

```
GET /concalls/list
```

### **Query Parameters**

| Parameter        | Type       | Required                    | Description                                                     |
| ---------------- | ---------- | --------------------------- | --------------------------------------------------------------- |
| `isin`           | string     | ✓ (for company-level fetch) | Company ISIN.                                                   |
| `page`           | integer    | No (default: 1)             | Page number.                                                    |
| `page_size`      | integer    | No (default: 20)            | Items per page.                                                 |
| `upcoming`       | boolean    | No (default: false)         | `true` → only future concalls.<br>`false` → completed concalls. |
| `mcap`           | string     | No                          | Ignored in v1.                                                  |
| `sectors`        | array      | No                          | Ignored in v1.                                                  |
| `tags_requested` | array<int> | No                          | Ignored in v1.                                                  |

### Example Request (Latest Completed Concall)

```
GET /concalls/list?isin=INE123A01016&page=1&page_size=1&upcoming=false
```

### Example Request (Upcoming Concall)

```
GET /concalls/list?isin=INE123A01016&upcoming=true
```

---

# 4. Response Schema

The API returns a wrapper object with pagination and data arrays.

### **Top-Level Response**

```json
{
  "pagination": {
    "total_results": 0,
    "total_pages": 0,
    "current_page": 0,
    "offset": 0
  },
  "active_filters": {
    "company_id": 0,
    "company_name": "string",
    "mcap": "all",
    "sectors": [
      { "name": "string", "sector_id": 0 }
    ],
    "tags_requested": [0]
  },
  "data": [
    {
      "company_info": {
        "name": "string",
        "sector": "string",
        "slug": "string"
      },
      "status": "Upcoming",
      "concall_event_time": "2025-12-03T19:09:44.471Z",
      "recording_link": "string",
      "management_consistency": "string"
    }
  ]
}
```

---

# 4.1 Field Details

## 📌 `pagination` Object

| Field           | Type   | Description                          |
| --------------- | ------ | ------------------------------------ |
| `total_results` | number | Total concalls matching the filters. |
| `total_pages`   | number | Pages available.                     |
| `current_page`  | number | Current page.                        |
| `offset`        | number | Offset for items.                    |

Used by our backend for pagination loops.

---

## 📌 `active_filters` Object

(Not used in v1 — informational only.)

---

## 📌 `data[]` — Concall Item

Each element represents a concall record.

### Schema

```json
{
  "company_info": {
    "name": "Company Name",
    "sector": "Industry Sector",
    "slug": "company-slug"
  },
  "status": "Completed",
  "concall_event_time": "2024-11-14T14:30:00Z",
  "recording_link": "https://...", 
  "management_consistency": "string or null"
}
```

### Meaning of Key Fields

| Field                    | Type                            | Used For                             |
| ------------------------ | ------------------------------- | ------------------------------------ |
| `company_info.name`      | string                          | Display name if DB mismatch.         |
| `company_info.sector`    | string                          | Auto-populating `sector_name` in DB. |
| `company_info.slug`      | string                          | Future deep-linking.                 |
| `status`                 | string (`Upcoming`/`Completed`) | Show concall stage in UI.            |
| `concall_event_time`     | ISO datetime                    | Sorting, “latest concall” detection. |
| `recording_link`         | string                          | Used in transcript + LLM pipeline.   |
| `management_consistency` | string/null                     | Optional quality metric.             |

---

# 5. How Our Backend Uses This API

## 5.1 Fetch Latest Concall (Core Logic)

```ts
async function fetchLatestConcallByIsin(isin: string) {
  const url =
    `${process.env.TIJORI_BASE_URL}/concalls/list?isin=${isin}&page=1&page_size=1&upcoming=false`;

  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${process.env.TIJORISTACK_API_TOKEN}`,
      Accept: "application/json"
    }
  });

  if (!res.ok) throw new Error("TijoriStack API Error");

  const body = await res.json();
  return body?.data?.[0] ?? null;
}
```

---

## 5.2 Database Mapping

### **Companies Table**

| Column        | Source                |
| ------------- | --------------------- |
| `isin`        | Request parameter     |
| `name`        | `company_info.name`   |
| `sector_name` | `company_info.sector` |
| `slug`        | `company_info.slug`   |

### **Concalls Table**

| Column                   | Source                            |
| ------------------------ | --------------------------------- |
| `company_id`             | Local FK                          |
| `concall_event_time`     | `concall_event_time`              |
| `status`                 | `status`                          |
| `recording_link`         | `recording_link`                  |
| `management_consistency` | `management_consistency`          |
| `raw_json`               | Entire object (for support/debug) |

---

# 6. Error Handling

### Retry Logic

* Retry on **5xx** and timeouts (max 3 attempts).
* Do NOT retry on **4xx** → log & fail gracefully.

### User Messaging

If concall fetch fails:

```
"Concall data provider temporarily unavailable. Please retry."
```

---

# 7. Environment Variables

```
TIJORISTACK_BASE_URL=https://www.tijoristack.ai/api/v1
TIJORISTACK_API_TOKEN=xxxxx
TIJORISTACK_DEFAULT_PAGE_SIZE=20
TIJORISTACK_TIMEOUT_MS=8000
```

---

# 8. Summary for Developers

### Supported Ops

* ✅ Fetch latest concall
* ✅ Fetch all past concalls (paginated)
* ✅ Fetch upcoming concalls
* 🔄 Everything is ISIN-driven

### Not Supported in v1

* No MCAP filters
* No tags
* No multi-company query
* No webhook or push model — **pull only**

---

If you'd like, I can also provide:

### ✔ OpenAPI 3.0 YAML spec

### ✔ A ready-to-deploy `TijoriClient` class (TypeScript or Python)

### ✔ Postman collection JSON

Just tell me what format you want next.


{
  "openapi": "3.0.0",
  "info": {
    "title": "Conference Call API",
    "version": "v1",
    "description": "API to retrieve filtered and paginated list of company conference calls."
  },
  "servers": [
    {
      "url": "/api/v1"
    }
  ],
  "x-combine": true,
  "components": {
    "securitySchemes": {
      "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Enter your API key as `Bearer {your_key}`"
      }
    }
  },
  "security": [
    {
      "ApiKeyAuth": []
    }
  ],
  "paths": {
    "/concalls/list": {
      "get": {
        "summary": "List Conference Calls",
        "description": "Returns a paginated list of conference calls with optional filtering.",
        "operationId": "listConferenceCalls",
        "parameters": [
          {
            "in": "query",
            "name": "page",
            "schema": {
              "type": "integer",
              "default": 1,
              "minimum": 1
            },
            "description": "Page number for pagination."
          },
          {
            "in": "query",
            "name": "offset",
            "schema": {
              "type": "integer",
              "minimum": 0
            },
            "description": "Row offset for pagination. Represents the number of records already retrieved. Returned in the response so the client can request the next batch."
          },
          {
            "in": "query",
            "name": "isin",
            "schema": {
              "type": "string"
            },
            "description": "Filter results by company ISIN."
          },
          {
            "in": "query",
            "name": "mcap",
            "schema": {
              "type": "string",
              "enum": [
                "all",
                "large",
                "mid",
                "small",
                "nano"
              ],
              "default": "all"
            },
            "description": "Market cap classification filter."
          },
          {
            "in": "query",
            "name": "sectors",
            "schema": {
              "type": "array",
              "items": {
                "type": "integer"
              }
            },
            "style": "form",
            "explode": true,
            "description": "List of sector IDs to filter by."
          },

          {
            "in": "query",
            "name": "tags",
            "schema": {
              "type": "array",
              "items": {
                "type": "integer"
              }
            },
            "style": "form",
            "explode": true,
            "description": "List of tag IDs to filter by."
          },

          {
            "in": "query",
            "name": "upcoming",
            "schema": {
              "type": "boolean",
              "default": false
            },
            "description": "If true, only return upcoming (future) concalls."
          },
          {
            "in": "query",
            "name": "page_size",
            "schema": {
              "type": "integer",
              "default": 20,
              "minimum": 1,
              "maximum": 100
            },
            "description": "Number of results per page."
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response with conference call data.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "pagination": {
                      "type": "object",
                      "properties": {
                        "total_results": {
                          "type": "integer"
                        },
                        "total_pages": {
                          "type": "integer"
                        },
                        "current_page": {
                          "type": "integer"
                        },
                        "offset": {
                          "type": "integer",
                          "description": "Row offset pointing to the start of this page’s data."
                        }
                      }
                    },
                    "active_filters": {
                      "type": "object",
                      "properties": {
                        "company_id": {
                          "type": "integer",
                          "nullable": true
                        },
                        "company_name": {
                          "type": "string",
                          "nullable": true
                        },
                        "mcap": {
                          "type": "string",
                          "enum": [
                            "all",
                            "large",
                            "mid",
                            "small",
                            "nano"
                          ]
                        },
                        "sectors": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                              "name": {
                                "type": "string"
                              },
                              "sector_id": {
                                "type": "integer"
                              }
                            }
                          }
                        },

                        "tags_requested": {
                          "type": "array",
                          "items": {
                            "type": "integer"
                          }
                        }
                      }
                    },
                    "data": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "company_info": {
                            "type": "object",
                            "properties": {
                              "name": {
                                "type": "string"
                              },
                              "sector": {
                                "type": "string"
                              },
                              "slug": {
                                "type": "string"
                              }
                            }
                          },
                          "status": {
                            "type": "string",
                            "enum": [
                              "Upcoming",
                              "recorded"
                            ]
                          },
                          "concall_event_time": {
                            "type": "string",
                            "format": "date-time"
                          },
                          "recording_link": {
                            "type": "string",
                            "format": "uri",
                            "nullable": true
                          },
                          "management_consistency": {
                            "type": "string",
                            "nullable": true
                          },
                          "summary_highlight": {
                            "type": "string",
                            "nullable": true
                          },
                          "transcript": {
                            "type": "string",
                            "format": "uri",
                            "nullable": true
                          },
                          "ai_summary": {
                            "type": "string",
                            "nullable": true
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid request or bad input.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          },
          "500": {
            "description": "Internal server error."
          }
        }
      }
    },

    "/concalls/tags": {
      "get": {
        "summary": "List Tags",
        "description": "Returns the available tags used for concall filtering along with IDs",
        "operationId": "listTags",
        "responses": {
          "200": {
            "description": "List of all tags.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "id": { "type": "integer" },
                      "name": { "type": "string" }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
