"""
OpenSearch Index Setup Script for ResearchAnalyst
Creates and configures OpenSearch index for company search
"""

import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Configuration
OPENSEARCH_ENDPOINT = ""  # e.g., "search-domain-abc123.us-east-1.es.amazonaws.com"
REGION = "us-east-1"  # Change to your OpenSearch domain region
INDEX_NAME = "companies_v1"

def get_opensearch_client():
    """Create OpenSearch client with AWS authentication"""
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        'es',
        session_token=credentials.token
    )
    
    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    return client

def create_index_mapping():
    """Create index mapping for companies search"""
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "analysis": {
                "analyzer": {
                    "company_name_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding",
                            "company_edge_ngram"
                        ]
                    },
                    "company_search_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding"
                        ]
                    }
                },
                "filter": {
                    "company_edge_ngram": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 20
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "company_id": {
                    "type": "long"
                },
                "isin": {
                    "type": "keyword"
                },
                "display_name": {
                    "type": "text",
                    "analyzer": "company_name_analyzer",
                    "search_analyzer": "company_search_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        },
                        "completion": {
                            "type": "completion"
                        }
                    }
                },
                "ticker": {
                    "type": "keyword",
                    "fields": {
                        "text": {
                            "type": "text"
                        }
                    }
                },
                "exchange": {
                    "type": "keyword"
                },
                "sector_name": {
                    "type": "keyword",
                    "fields": {
                        "text": {
                            "type": "text"
                        }
                    }
                },
                "slug": {
                    "type": "keyword"
                },
                "aliases": {
                    "type": "text",
                    "analyzer": "company_name_analyzer",
                    "search_analyzer": "company_search_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }
    }
    
    return mapping

def create_index(client):
    """Create the index with mapping"""
    try:
        if client.indices.exists(index=INDEX_NAME):
            print(f"⚠️  Index '{INDEX_NAME}' already exists")
            response = input("Do you want to delete and recreate it? (yes/no): ")
            if response.lower() == 'yes':
                client.indices.delete(index=INDEX_NAME)
                print(f"✓ Deleted existing index: {INDEX_NAME}")
            else:
                print("Skipping index creation")
                return False
        
        mapping = create_index_mapping()
        client.indices.create(index=INDEX_NAME, body=mapping)
        print(f"✓ Created index: {INDEX_NAME}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating index: {e}")
        raise

def insert_sample_documents(client):
    """Insert sample company documents for testing"""
    sample_companies = [
        {
            "company_id": 1,
            "isin": "INE123A01016",
            "display_name": "Tata Consultancy Services Ltd",
            "ticker": "TCS",
            "exchange": "NSE",
            "sector_name": "IT Services",
            "slug": "tcs",
            "aliases": ["TCS", "Tata Consultancy", "TCS Ltd"]
        },
        {
            "company_id": 2,
            "isin": "INE009A01021",
            "display_name": "Infosys Limited",
            "ticker": "INFY",
            "exchange": "NSE",
            "sector_name": "IT Services",
            "slug": "infosys",
            "aliases": ["Infosys", "INFY"]
        },
        {
            "company_id": 3,
            "isin": "INE002A01018",
            "display_name": "Reliance Industries Limited",
            "ticker": "RELIANCE",
            "exchange": "NSE",
            "sector_name": "Oil & Gas",
            "slug": "reliance",
            "aliases": ["Reliance", "RIL"]
        },
        {
            "company_id": 4,
            "isin": "INE040A01034",
            "display_name": "HDFC Bank Limited",
            "ticker": "HDFCBANK",
            "exchange": "NSE",
            "sector_name": "Banking",
            "slug": "hdfc-bank",
            "aliases": ["HDFC Bank", "HDFC"]
        }
    ]
    
    try:
        for company in sample_companies:
            client.index(
                index=INDEX_NAME,
                id=company['company_id'],
                body=company
            )
        
        # Refresh index to make documents searchable
        client.indices.refresh(index=INDEX_NAME)
        print(f"✓ Inserted {len(sample_companies)} sample documents")
        
    except Exception as e:
        print(f"✗ Error inserting sample documents: {e}")
        raise

def test_search(client):
    """Test search functionality"""
    test_queries = [
        "tcs",
        "reliance",
        "hdfc",
        "infosys"
    ]
    
    print("\n" + "="*60)
    print("TESTING SEARCH FUNCTIONALITY")
    print("="*60)
    
    for query in test_queries:
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "display_name^3",
                        "ticker^2",
                        "aliases^2",
                        "isin"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "size": 5
        }
        
        try:
            response = client.search(index=INDEX_NAME, body=search_body)
            hits = response['hits']['hits']
            
            print(f"\nQuery: '{query}' - Found {len(hits)} results")
            for hit in hits[:3]:
                source = hit['_source']
                print(f"  • {source['display_name']} ({source['ticker']}) - {source['isin']}")
                
        except Exception as e:
            print(f"✗ Error searching for '{query}': {e}")

def get_index_stats(client):
    """Get index statistics"""
    try:
        stats = client.indices.stats(index=INDEX_NAME)
        count = client.count(index=INDEX_NAME)
        
        print("\n" + "="*60)
        print("INDEX STATISTICS")
        print("="*60)
        print(f"Index Name: {INDEX_NAME}")
        print(f"Document Count: {count['count']}")
        print(f"Index Size: {stats['_all']['primaries']['store']['size_in_bytes'] / 1024:.2f} KB")
        print("="*60)
        
    except Exception as e:
        print(f"✗ Error getting index stats: {e}")

def print_connection_info():
    """Print connection information"""
    print("\n" + "="*60)
    print("OPENSEARCH CONNECTION INFO")
    print("="*60)
    print(f"Endpoint: {OPENSEARCH_ENDPOINT}")
    print(f"Region: {REGION}")
    print(f"Index: {INDEX_NAME}")
    print("\nSearch Example Query:")
    print("""
    POST /companies_v1/_search
    {
      "query": {
        "multi_match": {
          "query": "tata",
          "fields": ["display_name^3", "ticker^2", "aliases^2", "isin"],
          "type": "best_fields",
          "fuzziness": "AUTO"
        }
      },
      "size": 10
    }
    """)
    print("="*60)

def main():
    """Main setup function"""
    if not OPENSEARCH_ENDPOINT:
        print("❌ Please set OPENSEARCH_ENDPOINT in the script")
        print("   Example: search-domain-abc123.us-east-1.es.amazonaws.com")
        return False
    
    print(f"\n🚀 Starting OpenSearch setup for ResearchAnalyst...")
    print(f"Endpoint: {OPENSEARCH_ENDPOINT}")
    print(f"Index: {INDEX_NAME}\n")
    
    try:
        # Create client
        client = get_opensearch_client()
        print("✓ Connected to OpenSearch")
        
        # Create index
        if create_index(client):
            # Insert sample data
            response = input("\nDo you want to insert sample documents? (yes/no): ")
            if response.lower() == 'yes':
                insert_sample_documents(client)
                test_search(client)
                get_index_stats(client)
        
        print_connection_info()
        print("\n✅ OpenSearch setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Verify AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS User/Role: {identity['Arn']}\n")
    except Exception as e:
        print(f"❌ AWS credentials not configured properly: {e}")
        print("Please configure AWS CLI: aws configure")
        exit(1)
    
    main()

