"""
AWS Lambda Handler for TijoriStack Analysis API
Exposes transcript analysis as a REST API endpoint
"""

import os
import json
import csv
import requests
from typing import Dict, Any, Optional, List
from io import BytesIO

# Try different PDF libraries
try:
    import pypdf as PyPDF2
except ImportError:
    import PyPDF2

# Configuration from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBfpwXVA0L6r4ex3HR6-kRiGXw0d8_94jM")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
TIJORISTACK_API_KEY = os.getenv("TIJORISTACK_API_KEY", "67358aa613024c2fa6e0e5156fe50421")
TIJORISTACK_BASE_URL = "https://www.tijoristack.ai/api/v1"
MAX_TRANSCRIPTS = int(os.getenv("MAX_TRANSCRIPTS", "1"))

# For Lambda, we'll need to include Equity.csv in deployment or use S3
# For now, assume it's in the same directory
EQUITY_CSV_PATH = os.path.join(os.path.dirname(__file__), "Equity.csv")


# =============================================================================
# Core Functions (from original script)
# =============================================================================

def get_isin_from_csv(company_name: str) -> Optional[str]:
    """Find ISIN from Equity.csv"""
    try:
        with open(EQUITY_CSV_PATH, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            search_term = company_name.lower()
            
            for row in csv_reader:
                issuer_name = row.get('Issuer Name', '').lower()
                security_name = row.get('Security Name', '').lower()
                isin = row.get('ISIN No', '').strip()
                
                if search_term in issuer_name or search_term in security_name:
                    return isin
            
            # Try first word
            first_word = company_name.split()[0]
            with open(EQUITY_CSV_PATH, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    if first_word.lower() in row.get('Issuer Name', '').lower():
                        return row.get('ISIN No', '').strip()
        
        return None
    except Exception as e:
        raise Exception(f"CSV lookup error: {e}")


def download_pdf_text(url: str) -> str:
    """Download and parse PDF"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        pdf_file = BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception:
        return ""


def download_transcripts(isin: str, max_count: int) -> List[Dict[str, Any]]:
    """Download transcripts from Tijori"""
    url = f"{TIJORISTACK_BASE_URL}/concalls/list"
    params = {"isin": isin, "page": 1, "page_size": max_count, "upcoming": False}
    headers = {"Authorization": f"Bearer {TIJORISTACK_API_KEY}", "Accept": "application/json"}
    
    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    concalls = data.get("data", [])
    transcripts = []
    
    for concall in concalls:
        company_info = concall.get("company_info", {})
        transcript_url = concall.get("transcript")
        
        if transcript_url and transcript_url.startswith('http'):
            text = download_pdf_text(transcript_url)
            if text:
                transcripts.append({
                    "company": company_info.get('name'),
                    "sector": company_info.get('sector'),
                    "event_time": concall.get('concall_event_time'),
                    "text": text[:50000],  # Limit per transcript
                    "url": transcript_url
                })
    
    return transcripts


def analyze_with_gemini(user_prompt: str, company_name: str, isin: str, transcripts: List[Dict]) -> str:
    """Analyze transcripts with Gemini via direct HTTP API (no grpc!)"""
    
    # Build context
    context = f"Company: {company_name}\nISIN: {isin}\nTranscripts: {len(transcripts)}\n\n"
    for idx, trans in enumerate(transcripts, 1):
        context += f"\n═══ TRANSCRIPT {idx}: {trans.get('event_time')} ═══\n{trans.get('text')}\n"
    
    # Formatting instructions (prepended to user prompt)
    formatting_template = """
FORMATTING REQUIREMENTS:
Please maintain consistent formatting:
- Use bullet points (•) for main points
- Use sub-bullets (□) for supporting details
- Present numerical data in tables where possible
- Bold key metrics and percentages
- Use italics for management quotes
"""
    
    prompt = f"""You are an expert financial analyst for Indian stock market.

COMPANY: {company_name}
ISIN: {isin}

TRANSCRIPTS:
{context}

{formatting_template}

USER REQUEST:
{user_prompt}

Analyze the transcripts following the structure above. Be comprehensive but concise."""
    
    # Call Gemini REST API directly (no google-generativeai library!)
    url = f"{GEMINI_API_URL}?key={GOOGLE_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "maxOutputTokens": 4096
        }
    }
    
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text'].strip()


# =============================================================================
# Lambda Handler
# =============================================================================

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Expected input (API Gateway proxy format):
    {
      "body": {
        "company_name": "ICICI Bank",
        "prompt": "Analyze their earnings..."
      }
    }
    
    Or query parameters:
    ?company=ICICI+Bank&prompt=Analyze...
    
    Returns:
    {
      "statusCode": 200,
      "body": {
        "company": "ICICI Bank",
        "isin": "INE090A01021",
        "sector": "Banks",
        "transcripts_count": 1,
        "analysis": "..."
      }
    }
    """
    
    try:
        # Parse input
        if event.get('body'):
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            # Try query parameters
            body = event.get('queryStringParameters', {})
        
        company_name = body.get('company_name') or body.get('company')
        user_prompt = body.get('prompt') or body.get('question', 'Analyze the earnings concalls')
        
        if not company_name:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "company_name is required"})
            }
        
        # STEP 1: Get ISIN
        isin = get_isin_from_csv(company_name)
        if not isin:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"ISIN not found for {company_name}"})
            }
        
        # STEP 2: Download transcripts
        transcripts = download_transcripts(isin, MAX_TRANSCRIPTS)
        if len(transcripts) == 0:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "No transcripts available",
                    "company": company_name,
                    "isin": isin
                })
            }
        
        # STEP 3: Analyze
        analysis = analyze_with_gemini(user_prompt, company_name, isin, transcripts)
        
        # STEP 4: Return results
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  # Enable CORS
            },
            "body": json.dumps({
                "company": company_name,
                "isin": isin,
                "sector": transcripts[0].get('sector'),
                "transcripts_count": len(transcripts),
                "transcript_dates": [t.get('event_time') for t in transcripts],
                "analysis": analysis
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "body": json.dumps({
            "company_name": "AIA engineering",
            "prompt": "Analyze their Q2 performance"
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(json.loads(result['body']), indent=2))

