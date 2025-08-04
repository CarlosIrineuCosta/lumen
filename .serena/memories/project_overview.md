# Lumen Photography Platform - Project Overview

## Purpose
Lumen is a professional photography platform designed as "Instagram for Professional Photography" with a focus on artistic photography networking. It facilitates connections between photographers and models while maintaining a clean, ad-free experience without algorithmic manipulation.

## Core Business Principles
- **NO ADS EVER**: Clean, distraction-free photography experience
- **NO ALGORITHMIC PLACEMENT**: Chronological, user-controlled content discovery
- **PEOPLE-FIRST DISCOVERY**: Find photographers/models, not just browse images
- **PROFESSIONAL NETWORKING**: Real-world connections via GPS proximity
- **SUBSCRIPTION MODEL**: $5-150/year, no data exploitation or engagement manipulation

## Project Status
**Current Phase**: MVP Development
- **COMPLETED**: Firebase authentication, user avatars, backend models, 500px-style gallery framework
- **IN PROGRESS**: Backend server startup, database initialization
- **NEXT**: Image upload, user profiles, photo stream display

## Architecture Overview
**Microservices architecture deployed on Google Cloud:**

### Backend
- **Framework**: FastAPI 0.104.1 with Python 3.11
- **Database**: Cloud SQL PostgreSQL with flexible JSONB schema
- **Authentication**: Firebase Admin SDK + Client SDK
- **Storage**: Google Cloud Storage for images
- **ORM**: SQLAlchemy 2.0.23 with Alembic migrations
- **API Documentation**: Auto-generated via FastAPI (/docs, /redoc)

### Frontend  
- **Base**: HTML/CSS/JavaScript with jQuery
- **Gallery**: Justified Gallery library (500px-style mosaic layout)
- **Authentication**: Firebase Client SDK
- **Features**: Dark mode interface, responsive design, lightbox with metadata

### Infrastructure
- **Platform**: Google Cloud Platform
- **Container**: Docker with Cloud Run deployment
- **Monitoring**: Prometheus + Google Cloud Monitoring
- **Cost Control**: Daily budget monitoring ($3-7/day target)
- **Network**: Accessible via Tailscale (100.106.201.33)

## Database Schema Highlights
- **Users**: Flexible JSONB profiles with mandatory model fields (gender, age, height, weight)
- **Photos**: Collaborative tagging, metadata, privacy controls
- **Cities**: ~2500 geopolitically relevant locations
- **Specialties**: Art-focused categories (Portrait, Fashion, Lifestyle, Fitness, Pole Dance, Bikini)

## Key Features (MVP)
1. **Authentication**: Firebase Google OAuth with user avatars
2. **Image Upload**: Drag & drop with Firebase Storage integration
3. **User Profiles**: Flexible data with model-specific mandatory fields
4. **Photo Stream**: Chronological feed with 500px-style layout
5. **Discovery Modes**: Latest, Photographers, Models, Nearby, Collaborations
6. **Professional Focus**: Photographer/model networking without engagement manipulation

## Development Environment
- **Development OS**: Linux (accessible via Tailscale network)
- **Access**: Direct access from any device connected to Tailscale mesh network
- **No Mocks Policy**: All functionality implements real services, no temporary workarounds