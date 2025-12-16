"""
Cognito JWT Authentication and User Sync
Verifies JWT tokens and syncs users with database
"""

import os
import json
import time
import requests
from jose import jwt, JWTError
from typing import Optional, Dict
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration (from environment variables)
COGNITO_REGION = os.getenv('COGNITO_REGION', 'ap-south-1')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID', 'ap-south-1_1lUBZPVma')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID', '4odpufu4q9mp1lltmpuus1iqa7')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'researchanalyst-db.cle6mqs82txq.ap-south-1.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Nokia#5300')
}

# Cache for JWKS (JSON Web Key Set)
_jwks_cache = None
_jwks_cache_time = 0
JWKS_CACHE_DURATION = 3600  # 1 hour


def get_jwks():
    """Get JSON Web Key Set from Cognito"""
    global _jwks_cache, _jwks_cache_time
    
    # Return cached JWKS if still valid
    if _jwks_cache and (time.time() - _jwks_cache_time) < JWKS_CACHE_DURATION:
        return _jwks_cache
    
    # Fetch new JWKS
    jwks_url = f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json'
    
    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = time.time()
        return _jwks_cache
    except Exception as e:
        raise Exception(f"Failed to fetch JWKS: {e}")


def verify_jwt_token(token: str) -> Optional[Dict]:
    """
    Verify Cognito JWT token
    
    Args:
        token: JWT token string from Authorization header
    
    Returns:
        Dict with user claims if valid, None if invalid
    """
    
    if not COGNITO_USER_POOL_ID or not COGNITO_APP_CLIENT_ID:
        raise Exception("Cognito configuration missing (USER_POOL_ID or APP_CLIENT_ID)")
    
    try:
        # Get JWKS
        jwks = get_jwks()
        
        # Get the key id from token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        if not kid:
            return None
        
        # Find the matching key
        key = None
        for jwk in jwks.get('keys', []):
            if jwk['kid'] == kid:
                key = jwk
                break
        
        if not key:
            return None
        
        # Verify and decode token
        claims = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            audience=COGNITO_APP_CLIENT_ID,
            issuer=f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}'
        )
        
        # Check token expiration
        if claims.get('exp', 0) < time.time():
            return None
        
        return claims
        
    except JWTError as e:
        print(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


def get_or_create_user(claims: Dict) -> Optional[Dict]:
    """
    Get existing user or create new user from Cognito claims
    
    Args:
        claims: JWT claims dictionary
    
    Returns:
        User dict from database
    """
    
    cognito_sub = claims.get('sub')
    email = claims.get('email')
    
    if not cognito_sub or not email:
        return None
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Try to find existing user by cognito_sub
        cursor.execute(
            "SELECT * FROM users WHERE cognito_sub = %s",
            (cognito_sub,)
        )
        user = cursor.fetchone()
        
        if user:
            # User exists - update email if changed
            if user['email'] != email:
                cursor.execute(
                    """
                    UPDATE users 
                    SET email = %s, updated_at = now() 
                    WHERE cognito_sub = %s
                    RETURNING *
                    """,
                    (email, cognito_sub)
                )
                user = cursor.fetchone()
                conn.commit()
        else:
            # Create new user
            cursor.execute(
                """
                INSERT INTO users (email, cognito_sub, plan_tier)
                VALUES (%s, %s, 'trial')
                RETURNING *
                """,
                (email, cognito_sub)
            )
            user = cursor.fetchone()
            conn.commit()
            print(f"✓ Created new user: {email}")
        
        cursor.close()
        conn.close()
        
        # Convert to regular dict
        return dict(user) if user else None
        
    except Exception as e:
        print(f"Database error: {e}")
        return None


def authenticate_request(authorization_header: str) -> Optional[Dict]:
    """
    Authenticate API request using JWT token
    
    Args:
        authorization_header: Full Authorization header (e.g., "Bearer eyJhbGci...")
    
    Returns:
        User dict if authenticated, None if not
    """
    
    if not authorization_header:
        return None
    
    # Extract token from "Bearer <token>"
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    token = parts[1]
    
    # Verify JWT
    claims = verify_jwt_token(token)
    if not claims:
        return None
    
    # Get or create user in database
    user = get_or_create_user(claims)
    
    return user


# Example usage function
def example_lambda_handler(event, context):
    """
    Example Lambda function handler with Cognito auth
    
    This shows how to use the auth in your Lambda functions
    """
    
    # Extract Authorization header
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization') or headers.get('authorization')
    
    if not auth_header:
        return {
            'statusCode': 401,
            'body': json.dumps({
                'error_code': 'UNAUTHENTICATED',
                'message': 'Missing Authorization header'
            })
        }
    
    # Authenticate
    user = authenticate_request(auth_header)
    
    if not user:
        return {
            'statusCode': 401,
            'body': json.dumps({
                'error_code': 'UNAUTHENTICATED',
                'message': 'Invalid or expired token'
            })
        }
    
    # User is authenticated! Proceed with your logic
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Hello {user["email"]}!',
            'user_id': str(user['id']),
            'plan_tier': user['plan_tier']
        })
    }


if __name__ == "__main__":
    """
    Test script - run locally to test authentication
    """
    print("="*60)
    print("Cognito Authentication Test")
    print("="*60)
    
    # Check configuration
    if not COGNITO_USER_POOL_ID:
        print("❌ COGNITO_USER_POOL_ID not set")
        print("   Set it with: export COGNITO_USER_POOL_ID='ap-south-1_xxxxxx'")
        exit(1)
    
    if not COGNITO_APP_CLIENT_ID:
        print("❌ COGNITO_APP_CLIENT_ID not set")
        print("   Set it with: export COGNITO_APP_CLIENT_ID='xxxxxx'")
        exit(1)
    
    print(f"User Pool ID: {COGNITO_USER_POOL_ID}")
    print(f"App Client ID: {COGNITO_APP_CLIENT_ID}")
    print(f"Region: {COGNITO_REGION}")
    print()
    
    # Test JWKS fetch
    print("Testing JWKS fetch...")
    try:
        jwks = get_jwks()
        print(f"✓ JWKS loaded successfully ({len(jwks.get('keys', []))} keys)")
    except Exception as e:
        print(f"✗ Failed to load JWKS: {e}")
        exit(1)
    
    # Prompt for token
    print("\nTo test authentication:")
    print("1. Login to Cognito Hosted UI")
    print("2. Copy the id_token from URL")
    print("3. Run this script with token:")
    print("   python3 cognito_auth.py")
    print()
    
    token = input("Paste your JWT token (or press Enter to skip): ").strip()
    
    if token:
        print("\nVerifying token...")
        claims = verify_jwt_token(token)
        
        if claims:
            print("✓ Token is valid!")
            print(f"  User: {claims.get('email')}")
            print(f"  Sub: {claims.get('sub')}")
            print(f"  Expires: {time.ctime(claims.get('exp', 0))}")
            
            print("\nSyncing with database...")
            user = get_or_create_user(claims)
            
            if user:
                print("✓ User synced to database!")
                print(f"  ID: {user['id']}")
                print(f"  Email: {user['email']}")
                print(f"  Plan: {user['plan_tier']}")
            else:
                print("✗ Failed to sync user")
        else:
            print("✗ Token is invalid or expired")
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

