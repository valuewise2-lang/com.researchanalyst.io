#!/bin/bash
# Run this script in AWS CloudShell to setup the database
# Region: ap-south-1

set -e  # Exit on error

echo "============================================================"
echo "ResearchAnalyst Database Setup - AWS CloudShell"
echo "============================================================"

# Configuration
DB_HOST="researchanalyst-db.cle6mqs82txq.ap-south-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="researchanalyst"
DB_USER="postgres"
DB_PASSWORD="Nokia#5300"  # Change this if needed

# Check if psql is installed
echo ""
echo "1. Checking PostgreSQL client..."
if ! command -v psql &> /dev/null; then
    echo "   Installing PostgreSQL client..."
    sudo yum install -y postgresql15
    echo "   ✓ PostgreSQL client installed"
else
    echo "   ✓ PostgreSQL client already installed"
fi

# Test connection
echo ""
echo "2. Testing database connection..."
export PGPASSWORD="$DB_PASSWORD"

if psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -p "$DB_PORT" -c "SELECT version();" > /dev/null 2>&1; then
    echo "   ✓ Connection successful!"
else
    echo "   ✗ Connection failed!"
    echo "   Please check:"
    echo "     - RDS endpoint is correct"
    echo "     - Database password is correct"
    echo "     - Security group allows CloudShell IP (add 0.0.0.0/0 temporarily)"
    unset PGPASSWORD
    exit 1
fi

# Check if migration file exists
echo ""
echo "3. Checking for migration file..."
if [ ! -f "db_migration.sql" ]; then
    echo "   ✗ Migration file not found!"
    echo "   Please upload db_migration.sql to CloudShell:"
    echo "     1. Click 'Actions' → 'Upload file'"
    echo "     2. Select db_migration.sql"
    echo "     3. Run this script again"
    unset PGPASSWORD
    exit 1
fi
echo "   ✓ Migration file found"

# Run migration
echo ""
echo "4. Running migration..."
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -p "$DB_PORT" -f db_migration.sql

if [ $? -eq 0 ]; then
    echo "   ✓ Migration completed successfully!"
else
    echo "   ✗ Migration failed!"
    unset PGPASSWORD
    exit 1
fi

# Verify tables
echo ""
echo "5. Verifying tables created..."
echo ""
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -p "$DB_PORT" -c "\dt"

# Count tables
TABLE_COUNT=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -p "$DB_PORT" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)

echo ""
echo "============================================================"
if [ "$TABLE_COUNT" -ge 6 ]; then
    echo "✅ Database setup complete!"
    echo "============================================================"
    echo "Tables created: $TABLE_COUNT"
    echo ""
    echo "Expected tables:"
    echo "  ✓ users"
    echo "  ✓ companies"
    echo "  ✓ watchlists"
    echo "  ✓ watchlist_items"
    echo "  ✓ concalls"
    echo "  ✓ files"
    echo ""
    echo "Next steps:"
    echo "  1. Setup S3 bucket (run: bash setup_s3.sh)"
    echo "  2. Setup OpenSearch (run: bash setup_opensearch.sh)"
else
    echo "⚠️  Setup completed but expected tables not found"
    echo "============================================================"
    echo "Tables found: $TABLE_COUNT (expected: 6)"
fi
echo "============================================================"

# Clean up
unset PGPASSWORD

