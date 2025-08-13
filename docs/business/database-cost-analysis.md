# Database Cost Analysis

## Test Scenario: 100 users, 50 photos/user/month = 5,000 photos/month

### Storage Costs (Same for Both Options)
- 5,000 photos × 2MB average = 10GB/month
- Google Cloud Storage: ~$0.20/month

### Database Options Compared

#### Option A: PostgreSQL (Cloud SQL) - CHOSEN
**Monthly Costs:**
- Smallest instance (db-f1-micro): $7.67/month
- Storage (10GB): $1.70/month
- **Total Database: ~$9.40/month**

**Benefits:**
- Better complex queries for photography platform
- ACID transactions for data integrity
- Standard SQL for easier development
- Better scaling for professional features
- Existing models already built for PostgreSQL

#### Option B: Firestore (Alternative)
**Monthly Costs:**
- Document reads (~50,000/month): $0.18/month
- Document writes (~5,000/month): $0.54/month
- Storage (1GB): $0.18/month
- **Total Database: ~$0.90/month**

**Limitations:**
- Limited query capabilities
- NoSQL learning curve
- Less suitable for complex photography metadata

### Decision: PostgreSQL Selected

**Cost Difference:** $8.50/month more expensive than Firestore

**Rationale:**
1. Database infrastructure already configured for PostgreSQL
2. Models already built for relational structure
3. Professional photography platform needs complex queries
4. Better long-term scalability for advanced features
5. $8.50/month acceptable for better architecture

**Cost Scaling:**
- At 100 users: PostgreSQL is 10x more expensive
- At 1,000+ users: PostgreSQL becomes more cost-effective
- Break-even point: ~500-750 active users

**Date:** 2025-08-04
**Status:** Implemented