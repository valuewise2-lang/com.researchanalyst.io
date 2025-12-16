"""
S3 Bucket Setup Script for ResearchAnalyst
Creates and configures S3 bucket with proper folder structure and policies
"""

import boto3
import json
from botocore.exceptions import ClientError

# Configuration
BUCKET_NAME = "researchanalyst-storage"
REGION = "us-east-1"  # Change to your preferred region

def create_s3_bucket():
    """Create S3 bucket with proper configuration"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        # Create bucket
        if REGION == 'us-east-1':
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3_client.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': REGION}
            )
        print(f"✓ Created S3 bucket: {BUCKET_NAME}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"✓ Bucket {BUCKET_NAME} already exists and is owned by you")
        else:
            print(f"✗ Error creating bucket: {e}")
            raise

def enable_versioning():
    """Enable versioning on the bucket"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        s3_client.put_bucket_versioning(
            Bucket=BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"✓ Enabled versioning on {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error enabling versioning: {e}")
        raise

def configure_lifecycle():
    """Configure lifecycle policy for automatic cleanup"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    lifecycle_policy = {
        'Rules': [
            {
                'Id': 'DeleteOldExports',
                'Status': 'Enabled',
                'Prefix': 'exports/',
                'Expiration': {'Days': 7},
                'NoncurrentVersionExpiration': {'NoncurrentDays': 3}
            },
            {
                'Id': 'TransitionOldLogs',
                'Status': 'Enabled',
                'Prefix': 'logs/',
                'Transitions': [
                    {
                        'Days': 30,
                        'StorageClass': 'STANDARD_IA'
                    },
                    {
                        'Days': 90,
                        'StorageClass': 'GLACIER'
                    }
                ]
            }
        ]
    }
    
    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=BUCKET_NAME,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"✓ Configured lifecycle policy on {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error configuring lifecycle: {e}")
        raise

def configure_cors():
    """Configure CORS for frontend access"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'HEAD'],
                'AllowedOrigins': ['*'],  # Update with your frontend domain in production
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=BUCKET_NAME,
            CORSConfiguration=cors_configuration
        )
        print(f"✓ Configured CORS on {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error configuring CORS: {e}")
        raise

def configure_encryption():
    """Enable default encryption"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        s3_client.put_bucket_encryption(
            Bucket=BUCKET_NAME,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        },
                        'BucketKeyEnabled': True
                    }
                ]
            }
        )
        print(f"✓ Enabled encryption on {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error enabling encryption: {e}")
        raise

def block_public_access():
    """Block all public access"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        s3_client.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"✓ Configured public access block on {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error blocking public access: {e}")
        raise

def create_folder_structure():
    """Create logical folder structure"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    folders = [
        'transcripts/',
        'audio/',
        'company-outputs/',
        'sector-outputs/',
        'exports/',
        'logs/app/'
    ]
    
    for folder in folders:
        try:
            s3_client.put_object(Bucket=BUCKET_NAME, Key=folder)
            print(f"✓ Created folder: {folder}")
        except ClientError as e:
            print(f"✗ Error creating folder {folder}: {e}")

def print_bucket_info():
    """Print bucket information"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    print("\n" + "="*60)
    print("S3 BUCKET CONFIGURATION SUMMARY")
    print("="*60)
    print(f"Bucket Name: {BUCKET_NAME}")
    print(f"Region: {REGION}")
    print(f"Bucket URL: https://s3.console.aws.amazon.com/s3/buckets/{BUCKET_NAME}")
    print("\nFolder Structure:")
    print("  - transcripts/      (stores transcript JSON files)")
    print("  - audio/            (stores audio recordings)")
    print("  - company-outputs/  (stores analysis outputs)")
    print("  - sector-outputs/   (stores sector-level analyses)")
    print("  - exports/          (stores user exports, 7-day TTL)")
    print("  - logs/app/         (stores application logs)")
    print("\nSecurity:")
    print("  ✓ Versioning enabled")
    print("  ✓ Encryption at rest (AES256)")
    print("  ✓ Public access blocked")
    print("  ✓ CORS configured")
    print("  ✓ Lifecycle policies active")
    print("="*60)

def main():
    """Main setup function"""
    print(f"\n🚀 Starting S3 setup for ResearchAnalyst...")
    print(f"Bucket: {BUCKET_NAME} | Region: {REGION}\n")
    
    try:
        create_s3_bucket()
        enable_versioning()
        configure_encryption()
        block_public_access()
        configure_cors()
        configure_lifecycle()
        create_folder_structure()
        print_bucket_info()
        
        print("\n✅ S3 setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Verify AWS credentials are configured
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

