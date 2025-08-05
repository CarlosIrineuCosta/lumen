# Lumen Photography Platform - Project Vision

## Overview

Lumen is a professional photography platform designed as an ethical alternative to Instagram, prioritizing photographers' artistic freedom, professional networking, and quality over engagement metrics. It serves as a censorship-free portfolio and collaboration platform for photographers and models worldwide.

**Project Location**: `L:\projects\wasenet\`
**Development Docs**: Check `/docs/` directory for detailed technical (CODE-*) and strategic (STRATEGY-*) documentation

## Core Philosophy

### Fundamental Principles
- **NO ADS EVER** - Revenue through subscriptions, not attention exploitation
- **NO ALGORITHMIC MANIPULATION** - Chronological content, user-controlled discovery
- **PHOTOGRAPHER-FIRST** - Built for professionals, not influencers
- **UNCENSORED ARTISTIC EXPRESSION** - Support for artistic nudity and professional photography
- **PEOPLE-FIRST DISCOVERY** - Find and connect with photographers/models, not just browse images

### Key Differentiators
1. **Professional Networking**: GPS-based discovery for real-world collaborations
2. **Portfolio Focus**: Professional presentation tools, not engagement metrics
3. **Fair Moderation**: Clear standards with warning systems and appeals
4. **Data Ownership**: Users can export all their data and connections
5. **Quality Standards**: Paid membership prevents spam and maintains professionalism

## Technical Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.11) - High-performance async API framework
- **Frontend**: Vanilla JavaScript with Progressive Web App capabilities
- **Database**: PostgreSQL with JSONB fields for flexible schema evolution
- **Authentication**: Google OAuth via Firebase Auth (authentication only)
- **Storage**: Google Cloud Storage for images (NOT Firebase Storage)
- **Infrastructure**: Google Cloud Platform (Cloud Run, Cloud SQL)
- **Image Processing**: MozJPEG/Guetzli compression pipeline for quality optimization

### Data Architecture
1. **Authentication Layer**: Firebase handles Google OAuth and JWT tokens
2. **User Profiles**: PostgreSQL database with rich profile data and JSONB flexibility
3. **Image Storage**: Google Cloud Storage buckets with multiple compression formats
4. **Relationships**: PostgreSQL for all user connections, likes, and interactions

### Key Design Decisions
- **PostgreSQL over NoSQL**: Structured queries needed for geographic search and relationships
- **Vanilla JS Frontend**: Simplicity and performance over framework complexity
- **Multiple Image Formats**: Thumbnail, web, portfolio, and 4K TV quality versions
- **JSONB Fields**: Future-proof schema allowing feature expansion without migrations

## Business Model

### Subscription Tiers
1. **Basic** ($5/month): Platform access, uncensored posting, basic networking
2. **Portfolio** ($10/month): Advanced portfolio tools, priority support
3. **Advisor** ($150/year): Platform development input, early features
4. **Stakeholder** ($1000+/year): Strategic direction influence

### Revenue Strategy
- Subscription-based model ensuring user alignment
- No advertising or data selling
- Future: Competition fees, print services, gallery partnerships
- Target: 1000 users = $60-120K annual revenue at <$1000 infrastructure cost

## User Experience Vision

### Core Features
1. **Mosaic Gallery Display**: 500px-style Justified Gallery respecting image proportions
2. **Discovery Modes**: Latest Work, Photographers, Models, Nearby (GPS), Open for Work
3. **Professional Tools**: Contract signing, model releases, travel coordination
4. **TV Integration**: 4K image display on large screens via HDMI/wireless
5. **Geographic Networking**: Find collaborators by location with privacy controls

### Content Standards
- **Allowed**: Artistic nudity, professional photography, LGBTQ+ inclusive content
- **Prohibited**: Pornographic content, AI-generated images, commercial spam
- **Moderation**: Community-driven with fair warning systems

## Target Audience

### Primary Users
- Professional photographers seeking uncensored portfolios
- Models needing professional networking and travel coordination
- Photography enthusiasts focused on quality over likes
- Creative professionals frustrated with algorithmic platforms

### Geographic Focus
- Initial markets: Brazil, Europe, Australia, United States, Japan
- Democratic countries with artistic freedom protections
- International photographer/model community (12,000+ existing network)

## Development Philosophy

### Technical Principles
- **Real Implementation Only**: No mocks or temporary solutions
- **User Privacy First**: Minimal data collection, maximum user control
- **Performance Matters**: Sub-2 second uploads, instant navigation
- **Mobile-First Design**: Responsive across all devices
- **Progressive Enhancement**: Core features work everywhere, advanced features when supported

### Quality Standards
- Professional-grade image handling and color accuracy
- Fair and transparent moderation processes
- Sustainable growth over viral scaling
- Community quality over user quantity

## Success Metrics

### Technical Targets
- Photo upload time: <2 seconds
- Gallery load time: <500ms
- 4K TV display support
- 99.9% uptime

### Business Targets
- Year 1: 1,000 paying users
- Monthly recurring revenue: $10,000+
- User retention: >80% monthly
- Infrastructure cost: <$100/month

### Community Goals
- High-quality photography standard
- Active professional networking
- International creative exchange
- Magazine-worthy content curation

## Future Vision

### Planned Expansions
1. **AI-Assisted Features**: Smart tagging, portfolio generation (not content creation)
2. **Professional Services**: Print fulfillment, gallery partnerships
3. **Educational Platform**: Workshops, tutorials, mentorship
4. **Travel Coordination**: Integrated planning for photo shoots
5. **NFT/Blockchain**: Optional photography ownership certificates

### Long-term Goals
- Become the default platform for professional photographers
- Bridge digital portfolios with physical gallery exhibitions
- Support photographer economic sustainability
- Preserve artistic photography culture

---

*This vision document outlines the unchanging core principles and architecture of Lumen. For current implementation status and detailed technical specifications, see the `/docs/` directory.*