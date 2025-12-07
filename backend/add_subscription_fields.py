#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Migration SQL
migration_sql = """
-- Migration: Add subscription fields to users table
-- Date: 2025-09-13

-- Add subscription and billing fields to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free',
ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'active',
ADD COLUMN IF NOT EXISTS subscription_data JSONB DEFAULT '{}';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_stripe_subscription ON users(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier);
"""

def run_migration():
    try:
        # Connect to database
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        # Execute migration
        print("Running subscription fields migration...")
        cur.execute(migration_sql)
        conn.commit()

        # Verify subscription fields were added
        subscription_fields = [
            'stripe_customer_id',
            'stripe_subscription_id',
            'subscription_tier',
            'subscription_status',
            'subscription_data'
        ]

        for field in subscription_fields:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = %s;
            """, (field,))
            result = cur.fetchone()

            if result:
                print(f"✅ {field} column added to users table")
            else:
                print(f"❌ {field} column not found in users table")

        # Verify indexes were created
        cur.execute("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'users' AND indexname IN (
                'idx_users_stripe_customer',
                'idx_users_stripe_subscription',
                'idx_users_subscription_tier'
            );
        """)
        indexes = cur.fetchall()
        print(f"✅ Created {len(indexes)} subscription indexes")

        cur.close()
        conn.close()
        print("Subscription migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()