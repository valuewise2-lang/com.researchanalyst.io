"""
Watchlists API Lambda Functions
Handles creating and retrieving user watchlists
"""

import os
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'researchanalyst-db.cle6mqs82txq.ap-south-1.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Nokia#5300')
}


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)


def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# =============================================================================
# POST /v1/watchlists - Create Watchlist
# =============================================================================

def create_watchlist(event, context):
    """
    POST /v1/watchlists
    
    Request body:
    {
      "user_id": "uuid-here",  # Can come from URL param or body
      "name": "My IT Stocks",
      "type": "NORMAL",  # or "SECTOR"
      "description": "My favorite IT companies"  # optional
    }
    
    Returns:
    {
      "statusCode": 201,
      "body": {
        "id": "watchlist-uuid",
        "user_id": "user-uuid",
        "name": "My IT Stocks",
        "type": "NORMAL",
        "description": "...",
        "created_at": "2025-12-13T10:00:00Z",
        "updated_at": "2025-12-13T10:00:00Z"
      }
    }
    """
    
    try:
        # Parse input
        if event.get('body'):
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = {}
        
        # Get user_id from multiple sources (flexible!)
        user_id = None
        
        # 1. From body
        user_id = body.get('user_id')
        
        # 2. From path parameters (/v1/users/{user_id}/watchlists)
        if not user_id and event.get('pathParameters'):
            user_id = event['pathParameters'].get('user_id')
        
        # 3. From query string (?user_id=xxx)
        if not user_id and event.get('queryStringParameters'):
            user_id = event['queryStringParameters'].get('user_id')
        
        # Validate required fields
        if not user_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "VALIDATION_ERROR",
                    "message": "user_id is required"
                })
            }
        
        name = body.get('name')
        if not name:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "VALIDATION_ERROR",
                    "message": "name is required"
                })
            }
        
        # Extract optional fields
        watchlist_type = body.get('type', 'NORMAL')  # Default to NORMAL
        description = body.get('description')
        
        # Validate type
        if watchlist_type not in ['NORMAL', 'SECTOR']:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "VALIDATION_ERROR",
                    "message": "type must be 'NORMAL' or 'SECTOR'"
                })
            }
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verify user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            cursor.close()
            conn.close()
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "NOT_FOUND",
                    "message": f"User {user_id} not found"
                })
            }
        
        # Create watchlist
        cursor.execute(
            """
            INSERT INTO watchlists (user_id, name, type, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, name, type, description, created_at, updated_at
            """,
            (user_id, name, watchlist_type, description)
        )
        
        watchlist = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Convert to dict and serialize dates
        watchlist_dict = dict(watchlist)
        
        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "id": str(watchlist_dict['id']),
                "user_id": str(watchlist_dict['user_id']),
                "name": watchlist_dict['name'],
                "type": watchlist_dict['type'],
                "description": watchlist_dict['description'],
                "created_at": watchlist_dict['created_at'].isoformat() if watchlist_dict['created_at'] else None,
                "updated_at": watchlist_dict['updated_at'].isoformat() if watchlist_dict['updated_at'] else None
            })
        }
        
    except psycopg2.Error as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error_code": "DATABASE_ERROR",
                "message": str(e)
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error_code": "INTERNAL_ERROR",
                "message": str(e)
            })
        }


# =============================================================================
# GET /v1/watchlists - Get User's Watchlists
# =============================================================================

def get_watchlists(event, context):
    """
    GET /v1/watchlists?user_id=uuid
    OR
    GET /v1/users/{user_id}/watchlists
    
    Returns:
    {
      "statusCode": 200,
      "body": {
        "items": [
          {
            "id": "watchlist-uuid",
            "user_id": "user-uuid",
            "name": "My IT Stocks",
            "type": "NORMAL",
            "description": "...",
            "created_at": "2025-12-13T10:00:00Z",
            "updated_at": "2025-12-13T10:00:00Z"
          }
        ],
        "total_count": 1
      }
    }
    """
    
    try:
        # Get user_id from multiple sources
        user_id = None
        
        # 1. From path parameters
        if event.get('pathParameters'):
            user_id = event['pathParameters'].get('user_id')
        
        # 2. From query string
        if not user_id and event.get('queryStringParameters'):
            user_id = event['queryStringParameters'].get('user_id')
        
        # Validate
        if not user_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "VALIDATION_ERROR",
                    "message": "user_id is required (as query param or path param)"
                })
            }
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verify user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            cursor.close()
            conn.close()
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "NOT_FOUND",
                    "message": f"User {user_id} not found"
                })
            }
        
        # Get all watchlists for user (ordered by creation date, newest first)
        cursor.execute(
            """
            SELECT id, user_id, name, type, description, created_at, updated_at
            FROM watchlists
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        
        watchlists = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to list of dicts
        items = []
        for wl in watchlists:
            items.append({
                "id": str(wl['id']),
                "user_id": str(wl['user_id']),
                "name": wl['name'],
                "type": wl['type'],
                "description": wl['description'],
                "created_at": wl['created_at'].isoformat() if wl['created_at'] else None,
                "updated_at": wl['updated_at'].isoformat() if wl['updated_at'] else None
            })
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "items": items,
                "total_count": len(items)
            })
        }
        
    except psycopg2.Error as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error_code": "DATABASE_ERROR",
                "message": str(e)
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error_code": "INTERNAL_ERROR",
                "message": str(e)
            })
        }


# =============================================================================
# GET /v1/watchlists/{watchlist_id} - Get Single Watchlist with Items
# =============================================================================

def get_watchlist_by_id(event, context):
    """
    GET /v1/watchlists/{watchlist_id}
    
    Returns watchlist with all its companies
    """
    
    try:
        watchlist_id = event['pathParameters'].get('watchlist_id')
        
        if not watchlist_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "VALIDATION_ERROR",
                    "message": "watchlist_id is required"
                })
            }
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get watchlist
        cursor.execute(
            """
            SELECT id, user_id, name, type, description, created_at, updated_at
            FROM watchlists
            WHERE id = %s
            """,
            (watchlist_id,)
        )
        
        watchlist = cursor.fetchone()
        
        if not watchlist:
            cursor.close()
            conn.close()
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "NOT_FOUND",
                    "message": f"Watchlist {watchlist_id} not found"
                })
            }
        
        # Get items in this watchlist
        cursor.execute(
            """
            SELECT 
                wi.id,
                wi.company_id,
                wi.stock_name,
                wi.stock_isin,
                wi.position_order,
                wi.last_analysis_file_id,
                wi.last_analysis_updated_at
            FROM watchlist_items wi
            WHERE wi.watchlist_id = %s
            ORDER BY wi.position_order, wi.created_at
            """,
            (watchlist_id,)
        )
        
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Build response
        response_data = {
            "id": str(watchlist['id']),
            "user_id": str(watchlist['user_id']),
            "name": watchlist['name'],
            "type": watchlist['type'],
            "description": watchlist['description'],
            "items": [
                {
                    "id": str(item['id']),
                    "company_id": item['company_id'],
                    "stock_name": item['stock_name'],
                    "stock_isin": item['stock_isin'],
                    "position_order": item['position_order'],
                    "last_analysis_file_id": str(item['last_analysis_file_id']) if item['last_analysis_file_id'] else None,
                    "last_analysis_updated_at": item['last_analysis_updated_at'].isoformat() if item['last_analysis_updated_at'] else None
                }
                for item in items
            ],
            "created_at": watchlist['created_at'].isoformat() if watchlist['created_at'] else None,
            "updated_at": watchlist['updated_at'].isoformat() if watchlist['updated_at'] else None
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error_code": "INTERNAL_ERROR",
                "message": str(e)
            })
        }


# =============================================================================
# POST /v1/watchlists/{watchlist_id}/items - Add Company to Watchlist
# =============================================================================

def add_company_to_watchlist(event, context):
    """
    POST /v1/watchlists/{watchlist_id}/items
    
    Request body:
    {
      "company_id": 123
    }
    OR
    {
      "isin": "INE090A01021"
    }
    
    Returns: 201 with created item
    """
    
    try:
        watchlist_id = event['pathParameters'].get('watchlist_id')
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        company_id = body.get('company_id')
        isin = body.get('isin')
        
        if not company_id and not isin:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "VALIDATION_ERROR",
                    "message": "Either company_id or isin is required"
                })
            }
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # If ISIN provided, look up company_id
        if isin and not company_id:
            cursor.execute("SELECT id FROM companies WHERE isin = %s", (isin,))
            company = cursor.fetchone()
            if company:
                company_id = company['id']
            else:
                cursor.close()
                conn.close()
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error_code": "NOT_FOUND",
                        "message": f"Company with ISIN {isin} not found"
                    })
                }
        
        # Get company details
        cursor.execute(
            "SELECT id, isin, display_name FROM companies WHERE id = %s",
            (company_id,)
        )
        company = cursor.fetchone()
        
        if not company:
            cursor.close()
            conn.close()
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error_code": "NOT_FOUND",
                    "message": f"Company {company_id} not found"
                })
            }
        
        # Get max position_order for this watchlist
        cursor.execute(
            "SELECT COALESCE(MAX(position_order), 0) + 1 as next_position FROM watchlist_items WHERE watchlist_id = %s",
            (watchlist_id,)
        )
        next_position = cursor.fetchone()['next_position']
        
        # Insert watchlist item
        cursor.execute(
            """
            INSERT INTO watchlist_items 
            (watchlist_id, company_id, stock_name, stock_isin, position_order)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, watchlist_id, company_id, stock_name, stock_isin, position_order, created_at
            """,
            (watchlist_id, company['id'], company['display_name'], company['isin'], next_position)
        )
        
        item = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "id": str(item['id']),
                "watchlist_id": str(item['watchlist_id']),
                "company_id": item['company_id'],
                "stock_name": item['stock_name'],
                "stock_isin": item['stock_isin'],
                "position_order": item['position_order'],
                "created_at": item['created_at'].isoformat() if item['created_at'] else None
            })
        }
        
    except psycopg2.IntegrityError as e:
        # Duplicate company in watchlist
        return {
            "statusCode": 409,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error_code": "CONFLICT",
                "message": "Company already in watchlist"
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error_code": "INTERNAL_ERROR",
                "message": str(e)
            })
        }


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    """Local testing"""
    
    print("="*60)
    print("Watchlists API Testing")
    print("="*60)
    
    # First, create a test user
    print("\n1. Creating test user...")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        """
        INSERT INTO users (email, plan_tier)
        VALUES ('test@researchanalyst.io', 'trial')
        ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
        RETURNING id, email
        """
    )
    test_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Test user: {test_user['email']} (ID: {test_user['id']})")
    
    # Test 1: Create watchlist
    print("\n2. Testing POST /v1/watchlists (Create Watchlist)...")
    test_create_event = {
        "body": json.dumps({
            "user_id": str(test_user['id']),
            "name": "My IT Stocks",
            "type": "NORMAL",
            "description": "Best IT companies in India"
        })
    }
    
    result = create_watchlist(test_create_event, None)
    print(f"Status: {result['statusCode']}")
    response_body = json.loads(result['body'])
    print(f"Response: {json.dumps(response_body, indent=2)}")
    
    if result['statusCode'] == 201:
        watchlist_id = response_body['id']
        print(f"✓ Watchlist created: {watchlist_id}")
        
        # Test 2: Get watchlists
        print("\n3. Testing GET /v1/watchlists (Get All Watchlists)...")
        test_get_event = {
            "queryStringParameters": {
                "user_id": str(test_user['id'])
            }
        }
        
        result = get_watchlists(test_get_event, None)
        print(f"Status: {result['statusCode']}")
        response_body = json.loads(result['body'])
        print(f"Found {response_body['total_count']} watchlists")
        print(f"Response: {json.dumps(response_body, indent=2)}")
        
        # Test 3: Get specific watchlist
        print("\n4. Testing GET /v1/watchlists/{id} (Get Watchlist Details)...")
        test_get_one_event = {
            "pathParameters": {
                "watchlist_id": watchlist_id
            }
        }
        
        result = get_watchlist_by_id(test_get_one_event, None)
        print(f"Status: {result['statusCode']}")
        response_body = json.loads(result['body'])
        print(f"Response: {json.dumps(response_body, indent=2)}")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

