# Waiting List & Landing Page System Requirements
**Date**: November 30, 2025
**For**: Lumen Photography Platform

---

## 🎯 Executive Summary

A comprehensive waiting list and landing page system to manage user invites, track interested users, and control platform access during early access phase.

---

## 1. Landing Page (LP) System

### 1.1 Public Landing Page
**Location**: `/` (root route when not authenticated)

**Sections Required**:
1. **Hero Section**
   - App logo and tagline
   - Hero image/video showcase
   - CTA: "Join Waiting List"
   - Preview of photo gallery features

2. **Features Overview**
   - AI-powered photo tagging
   - Professional portfolio management
   - Private cloud storage
   - Collaborative galleries
   - Series management

3. **How It Works**
   - Simple 3-step process
   - Visual walkthrough
   - Benefits emphasis

4. **Pricing Tiers** (Future)
   - Free tier (with limitations)
   - Pro tier (early bird pricing)
   - Enterprise tier

5. **Waiting List Signup**
   - Email capture form
   - Priority indicators (e.g., "You're #123 in line")
   - Social proof (joined by X photographers)

6. **Contact/Support**
   - FAQ section
   - Support email
   - Social media links

### 1.2 Technical Implementation

**Frontend Components**:
```javascript
// New module: frontend/js/modules/landing.js
window.LumenLanding = {
    init() { /* Initialize landing page */ },
    captureEmail(email) { /* Submit to waiting list */ },
    updatePosition(position) { /* Update queue position */ },
    showFeatures() { /* Interactive feature showcase */ }
}
```

**Backend API Endpoints**:
```python
# New file: backend/app/api/endpoints/waiting_list.py

@router.post("/api/v1/waiting-list/join")
async def join_waiting_list(email: str, name: str = None, referral: str = None)

@router.get("/api/v1/waiting-list/status/{email}")
async def get_waiting_list_status(email: str)

@router.get("/api/v1/waiting-list/count")
async def get_waiting_list_count()  // Public count
```

---

## 2. Waiting List Management System

### 2.1 Database Schema

**New Table**: `waiting_list_entries`
```sql
CREATE TABLE waiting_list_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    referral_code VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',  // pending, invited, registered, declined
    position INTEGER,
    priority_score INTEGER DEFAULT 0,  // For influencer/early supporters
    invited_at TIMESTAMP,
    invite_token VARCHAR(255) UNIQUE,
    invite_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB  -- Additional data
);
```

**Index Requirements**:
- Unique index on email
- Index on status
- Index on invited_at
- Index on position

### 2.2 Invite System Workflow

1. **User Joins Waiting List**
   ```
   User Email → Validation → Added to Queue → Email Confirmation → Position Assigned
   ```

2. **Invitation Process** (Admin controlled)
   ```
   Admin selects batch → Generate tokens → Send emails → Track responses
   ```

3. **Registration from Invite**
   ```
   Token Validation → Create Account → Remove from waiting list → Welcome email
   ```

### 2.3 Invite Token System

**Token Structure**:
- Secure random string (32 chars)
- One-time use
- Expires in 7 days
- Associated with email

**Admin Interface Requirements**:
```python
# New admin endpoints
@router.post("/api/v1/admin/waiting-list/invite-batch")
async def send_invites(email_list: List[str], message_template: str)

@router.get("/api/v1/admin/waiting-list/entries")
async def get_waiting_list_entries(status: str = None, limit: int = 100)

@router.post("/api/v1/admin/waiting-list/priority/{email}")
async def update_priority(email: str, priority_score: int)
```

---

## 3. Master List Management

### 3.1 Master List Features

**Admin Dashboard**:
- View all waiting list entries
- Filter by status, date, referral
- Sort by priority, position
- Search by name/email
- Export to CSV

**User Categories**:
1. **Regular Users**: General public
2. **Early Supporters**: First 100 signups
3. **Influencers**: Photographers with following
4. **Beta Testers**: Selected for testing
5. **Partners**: Business collaborators

### 3.2 Automated Notifications

**Email Templates**:
1. **Welcome to Waiting List**
   - Position in queue
   - Expected timeline
   - Feature teasers

2. **You're Invited!**
   - Personal invite link
   - Registration instructions
   - Welcome bonus info

3. **Reminder** (if not registered)
   - "Your invite expires in X days"
   - Re-send invite link

4. **Welcome to Lumen**
   - Onboarding guide
   - First steps tutorial
   - Support contact

---

## 4. Integration with Existing System

### 4.1 Authentication Modifications

**Current**: Direct Firebase auth
**New**: Waiting list validation for new users

```javascript
// Modified auth flow in auth.js
async function registerWithInvite(token, email, password) {
    // 1. Validate invite token
    const inviteValid = await LumenAPI.validateInvite(token);
    if (!inviteValid) {
        throw new Error('Invalid or expired invite');
    }

    // 2. Create Firebase account
    const user = await firebase.auth().createUserWithEmailAndPassword(email, password);

    // 3. Mark invite as used
    await LumenAPI.consumeInvite(token, user.uid);

    // 4. Continue with normal registration
    return user;
}
```

### 4.2 Configuration Management

**Environment Variables**:
```env
# Waiting List Settings
WAITING_LIST_ENABLED=true
INVITE_EXPIRY_DAYS=7
MAX_INVITES_PER_BATCH=100
INVITE_COOLDOWN_HOURS=24

# Email Settings
WAITING_LIST_EMAIL_TEMPLATE=templates/waiting_list.html
INVITE_EMAIL_TEMPLATE=templates/invite.html

# Admin Settings
WAITING_LIST_ADMIN_EMAILS=admin@lumen.app,founder@lumen.app
```

---

## 5. Launch Strategy

### Phase 1: Soft Launch (Week 1-2)
- Landing page goes live
- Waiting list opens for early supporters
- No invites sent yet
- Collect feedback from community

### Phase 2: Beta Testing (Week 3-4)
- Send first 100 invites
- Focus on photographers
- Gather bug reports
- Fix critical issues

### Phase 3: Gradual Rollout (Week 5-8)
- Send invites in batches of 50-100
- Monitor system stability
- Scale based on capacity
- Public launch announcement

### Phase 4: Public Launch (Week 9+)
- Remove waiting list
- Open registration
- Implement freemium model
- Marketing push

---

## 6. Success Metrics

### Landing Page Metrics
- **Conversion Rate**: Email signups / visitors (Target: 15-20%)
- **Bounce Rate**: < 40%
- **Time on Page**: > 2 minutes
- **Social Shares**: Track referral codes

### Waiting List Metrics
- **Growth Rate**: New signups per day (Target: 50-100/day)
- **Invite Acceptance**: Invites accepted / sent (Target: 60-80%)
- **Registration Conversion**: Accounts created / invites accepted (Target: 80-90%)

### System Metrics
- **Email Delivery Rate**: > 98%
- **Email Open Rate**: > 50%
- **Support Tickets**: < 5% of new users

---

## 7. Security Considerations

### Invite System Security
1. **Token Security**
   - Cryptographically secure random generation
   - Rate limiting on token validation
   - One-time use enforcement

2. **Email Verification**
   - Confirm email ownership
   - Prevent disposable emails
   - CAPTCHA on signup

3. **Rate Limiting**
   - Max 5 emails per IP per day
   - Max 1 signup per email
   - Invite cooldown periods

### Data Privacy
- GDPR compliant email handling
- Easy unsubscribe option
- Data deletion on request
- Clear privacy policy

---

## 8. Technical Dependencies

### New Packages Needed
```python
# Backend
fastapi-users>=0.12.0  # For invite management
jinja2>=3.1.0         # Email templates
aiosmt>=1.2.0         # Async email sending
```

### Frontend Changes
- New landing page module
- Invite validation logic
- Email capture forms
- Queue position display

---

## 9. Implementation Timeline

### Week 1: Core Infrastructure
- [ ] Create database schema
- [ ] Build basic API endpoints
- [ ] Design landing page mockups

### Week 2: Landing Page
- [ ] Implement landing page
- [ ] Create email signup forms
- [ ] Set up email templates

### Week 3: Admin System
- [ ] Build admin dashboard
- [ ] Implement invite generation
- [ ] Create batch invite system

### Week 4: Integration
- [ ] Modify auth flow
- [ ] Test full registration flow
- [ ] Set up analytics

### Week 5+: Launch
- [ ] Soft launch
- [ ] Monitor and iterate
- [ ] Gradual rollout

---

## 10. Budget Considerations

### Development Costs
- **Backend Development**: 40 hours
- **Frontend Development**: 30 hours
- **Email Templates**: 10 hours
- **Testing**: 20 hours
- **Total**: 100 hours (~$15,000 at agency rates)

### Operational Costs
- **Email Service**: $20/month (for 10,000 emails)
- **Analytics**: $0 (Google Analytics)
- **Hosting**: Existing infrastructure

---

## Conclusion

The waiting list and landing page system is crucial for:
1. **Controlled Growth**: Manage server resources and support capacity
2. **Quality Assurance**: Ensure good user experience from day one
3. **Marketing Buzz**: Create anticipation and exclusivity
4. **Feedback Collection**: Gather insights from early adopters

This system provides a professional onboarding experience while maintaining control over the platform's growth trajectory.

---

*Requirements created for Lumen Photography Platform*