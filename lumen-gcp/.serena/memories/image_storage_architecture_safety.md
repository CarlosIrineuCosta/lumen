# Image Storage Architecture & Safety Analysis

## CONFIRMED ARCHITECTURE (SAFE & INDUSTRY STANDARD)

### Storage Split
- **Google Cloud Storage**: Physical image files (.jpg, .png, .webp)
- **PostgreSQL**: Metadata records with URLs pointing to Cloud Storage
- **Binding**: PostgreSQL photo records contain Cloud Storage URLs

### Benefits Confirmed
- **Performance**: Fast text searches on PostgreSQL without scanning large blobs
- **Scalability**: Independent scaling of database vs file storage  
- **Cost**: Object storage ~$0.020/GB vs database storage ~$0.40/GB+
- **CDN**: Global image delivery via Google's edge network

## SECURITY IMPLEMENTATION

### Signed URLs Approach (APPROVED)
- Use Firebase signed URLs for secure image access
- Auth process: User clicks 1-2 pages for access (acceptable UX trade-off)
- Temporary, secure access without making files public
- Prevents direct URL access bypassing authentication

### Current Security Issue
- Current implementation uses public URLs: `https://storage.googleapis.com/{bucket}/{file}`
- **NEEDS FIXING**: Replace with signed URLs generation

## SOFT DELETE PATTERN (APPROVED)

### Implementation Strategy
```sql
-- Add to photos table
ALTER TABLE photos ADD COLUMN status VARCHAR(20) DEFAULT 'active';
ALTER TABLE photos ADD COLUMN deleted_at TIMESTAMP NULL;

-- Soft delete process
UPDATE photos SET status = 'pending_deletion', deleted_at = NOW() 
WHERE id = photo_id AND user_id = current_user;
```

### Benefits
- Immediate UI response (photo appears deleted instantly)
- Actual cleanup happens asynchronously
- Prevents broken references during cleanup process
- Maintains data consistency

## GARBAGE COLLECTION SYSTEM (REQUIRED)

### Background Cleanup Jobs
1. **Pending Deletion Processor** (every 5 minutes)
   - Query photos with status = 'pending_deletion'
   - Delete from Cloud Storage
   - Delete PostgreSQL record after successful file deletion

2. **Orphan File Reconciliation** (weekly/monthly)
   - List all Cloud Storage files
   - Check for corresponding active PostgreSQL records
   - Delete orphaned files (quarantine first, then permanent deletion)

### Consistency Safety
- Favor orphaned files over broken references
- Broken UI is immediate user problem
- Orphaned files are backend cleanup issue

## ACCOUNT LIFECYCLE POLICY (ETHICAL & TRANSPARENT)

### Payment Grace Period
- **1 Month**: Account goes offline (not accessible to public)
- **3 Months**: Account frozen (user can still recover by paying)
- **After 3 Months**: Complete account deletion

### Benefits
- **Ethical**: Accommodates travel, family problems, temporary financial issues
- **Transparent**: Clear timeline communicated to users
- **Anti-Ghost**: Prevents abandoned accounts cluttering system
- **Business**: Encourages payment while being understanding

### Implementation Requirements
```sql
-- Add to users table
ALTER TABLE users ADD COLUMN account_status VARCHAR(20) DEFAULT 'active';
ALTER TABLE users ADD COLUMN payment_due_date TIMESTAMP;
ALTER TABLE users ADD COLUMN frozen_date TIMESTAMP;
```

## IMPLEMENTATION PRIORITIES

### Phase 1: Security (HIGH PRIORITY)
- Replace public URLs with signed URLs in PhotoService
- Implement Firebase Security Rules

### Phase 2: Soft Delete (HIGH PRIORITY)  
- Add status/deleted_at columns to photos table
- Update API endpoints to use soft delete
- Filter deleted photos from all queries

### Phase 3: Garbage Collection (MEDIUM PRIORITY)
- Background job for pending deletion cleanup
- Orphan file reconciliation script

### Phase 4: Account Lifecycle (LOW PRIORITY)
- Payment tracking system
- Account status management
- Automated cleanup based on payment status

## SAFETY CONFIRMATION
✅ Architecture is safe with proper implementation
✅ Industry standard pattern (Instagram, Flickr, 500px use similar)
✅ Ethical account management approach
✅ Comprehensive garbage collection strategy