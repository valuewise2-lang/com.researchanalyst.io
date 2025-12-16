#!/bin/bash
# Setup S3 bucket in AWS CloudShell

set -e

echo "============================================================"
echo "ResearchAnalyst S3 Bucket Setup - AWS CloudShell"
echo "============================================================"

# Configuration
BUCKET_NAME="researchanalyst-storage"
REGION="ap-south-1"

echo ""
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo ""

# 1. Create bucket
echo "1. Creating S3 bucket..."
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION"
    echo "   ✓ Bucket created"
else
    echo "   ✓ Bucket already exists"
fi

# 2. Enable versioning
echo ""
echo "2. Enabling versioning..."
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled
echo "   ✓ Versioning enabled"

# 3. Enable encryption
echo ""
echo "3. Enabling encryption..."
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }'
echo "   ✓ Encryption enabled"

# 4. Block public access
echo ""
echo "4. Blocking public access..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
echo "   ✓ Public access blocked"

# 5. Configure CORS
echo ""
echo "5. Configuring CORS..."
cat > /tmp/cors.json << 'EOF'
{
    "CORSRules": [{
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }]
}
EOF

aws s3api put-bucket-cors \
    --bucket "$BUCKET_NAME" \
    --cors-configuration file:///tmp/cors.json
echo "   ✓ CORS configured"

# 6. Lifecycle policy
echo ""
echo "6. Configuring lifecycle policy..."
cat > /tmp/lifecycle.json << 'EOF'
{
    "Rules": [
        {
            "Id": "DeleteOldExports",
            "Status": "Enabled",
            "Prefix": "exports/",
            "Expiration": {
                "Days": 7
            }
        },
        {
            "Id": "TransitionOldLogs",
            "Status": "Enabled",
            "Prefix": "logs/",
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket "$BUCKET_NAME" \
    --lifecycle-configuration file:///tmp/lifecycle.json
echo "   ✓ Lifecycle policy configured"

# 7. Create folder structure
echo ""
echo "7. Creating folder structure..."
for folder in transcripts/ audio/ company-outputs/ sector-outputs/ exports/ logs/app/; do
    aws s3api put-object --bucket "$BUCKET_NAME" --key "$folder"
    echo "   ✓ Created: $folder"
done

# Verify
echo ""
echo "============================================================"
echo "✅ S3 Bucket Setup Complete!"
echo "============================================================"
echo ""
echo "Bucket: s3://$BUCKET_NAME"
echo "Region: $REGION"
echo ""
echo "Folder structure:"
aws s3 ls "s3://$BUCKET_NAME/"
echo ""
echo "Console: https://s3.console.aws.amazon.com/s3/buckets/$BUCKET_NAME"
echo "============================================================"


