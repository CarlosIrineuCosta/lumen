# Lumen Platform - Security & Infrastructure Addendum

## DDoS Protection Strategy

### Google Cloud Armor Configuration
- **Layer 7 DDoS protection** enabled for all endpoints
- **Rate limiting rules**:
  - Authentication endpoints: 5 requests/minute per IP
  - Upload endpoints: 10 requests/minute per user
  - Search/browse: 60 requests/minute per user
  - Image serving: 1000 requests/minute per IP (CDN backed)

### Additional Protection Layers
- **Cloudflare** as primary CDN and DDoS shield
- **ReCAPTCHA v3** for suspicious activity patterns
- **Progressive rate limiting**: Gradual restrictions for repeat offenders
- **Geographic filtering** during attacks (maintain core markets)

### Bot Detection
- Registration requires email verification
- Behavioral analysis on browsing patterns
- CAPTCHA triggered by:
  - Rapid page navigation
  - Multiple failed login attempts
  - Unusual upload patterns
  - Excessive API calls

## Scraping Prevention

### Image Protection
- **Dynamic URLs**: Session-based image URLs that expire
- **Watermarking options**:
  - Invisible watermarks for tracking
  - Optional visible watermarks for users
- **Right-click protection**: Educational message about copyright
- **Referrer checking**: Images only serve from platform domains

### API Security
- **JWT tokens** with short expiration (1 hour)
- **Refresh token** rotation
- **API key** per application (future mobile apps)
- **Request signing** for sensitive operations

### Legal Framework
- **DMCA agent** registration
- **Automated takedown** system
- **Three-strike policy** for scrapers
- **Terms of Service** explicitly prohibiting scraping

## Age Verification System

### Implementation (Steam/RedGifs Model)
```python
# Age gate configuration
AGE_GATE = {
    'minimum_age': 18,
    'cookie_duration': 30,  # days
    'legal_text': {
        'en': 'I confirm I am 18 or older (or legal age in my jurisdiction)',
        'pt': 'Confirmo que tenho 18 anos ou mais (ou idade legal em minha jurisdição)',
        'es': 'Confirmo que tengo 18 años o más (o la edad legal en mi jurisdicción)'
    }
}
```

### Compliance Approach
- **Cookie-based** verification (no account required to browse)
- **Account registration** requires age confirmation
- **Clear warnings** about artistic nudity content
- **Jurisdiction detection** via GeoIP (adjust minimum age if needed)

## NSFW Detection & Management

### AI-Powered Detection (Batch Processing)
- **Google Vision API** Safe Search detection
- **Confidence thresholds**:
  - Adult: 0.8+ → Auto-tag NSFW
  - Adult: 0.6-0.8 → Flag for review
  - Violence/Gore: Any level → Flag for review
  
### Manual Override System
- Users can dispute NSFW tags
- Trusted users can moderate (after 6 months + good standing)
- Appeals process for wrongly tagged content

### Display Logic
```javascript
// NSFW content display based on user settings
if (image.isNSFW) {
  switch(user.nsfwPreference) {
    case 'SHOW_ALL':
      return renderImage(image);
    case 'BLUR_NSFW':
      return renderBlurredImage(image, {clickToReveal: true});
    case 'HIDE_NSFW':
      return null; // Don't show at all
  }
}
```

## Infrastructure Scaling Plan

### Phase 1: Beta (0-200 users)
- **Single Region**: us-central1 (lowest cost)
- **Basic Setup**:
  - 1 Cloud SQL instance (db-f1-micro)
  - 1 App Engine instance (F1 class)
  - 1 Storage bucket
  - Monthly cost: ~$100

### Phase 2: Growth (200-1000 users)
- **Multi-Region CDN**: Global image delivery
- **Scaled Setup**:
  - Cloud SQL with read replica
  - 2-4 App Engine instances (autoscaling)
  - Multi-region storage
  - Monthly cost: ~$300-500

### Phase 3: Scale (1000+ users)
- **Full Global Infrastructure**:
  - Cloud SQL cluster with regional replicas
  - Kubernetes Engine for microservices
  - Global Load Balancer
  - Monthly cost: ~$1000+

## Monitoring & Alerts

### Key Metrics
- **Security Events**:
  - Failed login attempts
  - Unusual upload patterns
  - API abuse attempts
  - Scraping detection

- **Performance Metrics**:
  - Image upload times
  - Gallery load speed
  - Search response time
  - Database query performance

- **Business Metrics**:
  - New registrations
  - Active users (DAU/MAU)
  - Upload frequency
  - Storage growth rate

### Alert Thresholds
- DDoS attack indicators → Immediate
- Database performance degradation → 5 minutes
- Storage quota approaching → 24 hours
- Unusual user behavior patterns → 1 hour

## Calendar/Scheduling System Architecture

### Database Schema Addition
```sql
CREATE TABLE availability (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    location VARCHAR(100),
    availability_type ENUM('available', 'busy', 'traveling'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_schedules (
    id UUID PRIMARY KEY,
    photographer_id UUID REFERENCES users(id),
    model_id UUID REFERENCES users(id),
    proposed_date TIMESTAMP NOT NULL,
    duration_hours INTEGER,
    location VARCHAR(200),
    status ENUM('proposed', 'confirmed', 'completed', 'cancelled'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Calendar Features
- **Public View**: Month blocks (available/busy)
- **Connected View**: Specific dates and times
- **Timezone Handling**: All times stored in UTC
- **Conflict Detection**: Prevent double-booking
- **Weather Integration**: (Future) Weather warnings for outdoor shoots

## Beta Pricing Implementation

### Tiered System for Early Adopters
```python
BETA_PRICING = {
    'supporter': {
        'price': 25.00,
        'features': ['All features', 'Direct input on development', 'Lifetime 50% discount'],
        'target_users': 20-40
    },
    'early_bird': {
        'price': 10.00,
        'features': ['Full platform access', 'Founding member badge', 'Lifetime 25% discount'],
        'target_users': 100-150
    }
}
```

### Payment Processing
- **Stripe** integration (supports Brazilian PIX)
- **Regional payment methods**:
  - Credit/Debit cards (global)
  - PIX (Brazil)
  - SEPA (Europe)
  - Bank transfers (Japan)

## International Compliance

### Data Localization
- **EU Users**: GDPR compliance, data stays in EU
- **Brazilian Users**: LGPD compliance
- **US Users**: CCPA compliance (California)
- **Export Controls**: Block sanctioned countries

### Content Restrictions by Region
```python
REGIONAL_RESTRICTIONS = {
    'JP': {
        'blur_required': True,  # Japan specific requirements
        'min_age': 18
    },
    'SA': {
        'nudity_allowed': False,  # Saudi Arabia
        'min_age': 21
    },
    'DEFAULT': {
        'nudity_allowed': True,
        'min_age': 18
    }
}
```

### Legal Documentation
- **Terms of Service**: Multi-language
- **Privacy Policy**: GDPR/LGPD compliant
- **Community Guidelines**: Clear, with examples
- **Model Release Templates**: Optional but encouraged

## Emergency Response Procedures

### Security Incidents
1. **DDoS Attack**: Auto-scale, enable stricter rate limits
2. **Data Breach**: Immediate notification system, password resets
3. **Illegal Content**: Rapid takedown, law enforcement cooperation
4. **Account Compromise**: Automatic lockdown, recovery process

### Platform Issues
1. **Major Outage**: Status page, email notifications
2. **Data Loss**: Backup recovery (daily backups)
3. **Payment Issues**: Manual processing fallback
4. **Mass Exodus**: Export tools ready

---

*This addendum provides security, infrastructure, and compliance details for the Lumen platform. Integrate with main technical documentation.*