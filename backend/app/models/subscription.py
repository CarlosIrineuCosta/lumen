"""Subscription models for Lumen API"""

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    HOBBYIST = "hobbyist"
    PROFESSIONAL = "professional"
    STUDIO = "studio"

class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"

class SubscriptionFeatures(BaseModel):
    """Features available for each subscription tier"""
    monthly_uploads: int
    storage_gb: float
    collections_enabled: bool
    analytics_enabled: bool
    custom_domain: bool
    priority_support: bool
    api_access: bool
    team_members: int
    watermark_removal: bool

class SubscriptionPlan(BaseModel):
    """Subscription plan definition"""
    tier: SubscriptionTier
    name: str
    price_monthly: float
    price_yearly: float
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None
    features: SubscriptionFeatures
    description: str

class UserSubscription(BaseModel):
    """User's current subscription"""
    user_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    created_at: datetime
    updated_at: datetime

class CreateCheckoutSessionRequest(BaseModel):
    """Request to create Stripe checkout session"""
    tier: SubscriptionTier
    billing_cycle: str = "monthly"  # monthly or yearly
    success_url: str
    cancel_url: str

class StripeWebhookEvent(BaseModel):
    """Stripe webhook event data"""
    event_type: str
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    user_id: Optional[str] = None
    data: dict

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    SubscriptionTier.FREE: SubscriptionPlan(
        tier=SubscriptionTier.FREE,
        name="Free Trial",
        price_monthly=0.0,
        price_yearly=0.0,
        features=SubscriptionFeatures(
            monthly_uploads=10,
            storage_gb=1.0,
            collections_enabled=False,
            analytics_enabled=False,
            custom_domain=False,
            priority_support=False,
            api_access=False,
            team_members=1,
            watermark_removal=False
        ),
        description="14-day trial with basic features"
    ),
    SubscriptionTier.HOBBYIST: SubscriptionPlan(
        tier=SubscriptionTier.HOBBYIST,
        name="Hobbyist",
        price_monthly=9.0,
        price_yearly=90.0,
        features=SubscriptionFeatures(
            monthly_uploads=100,
            storage_gb=10.0,
            collections_enabled=True,
            analytics_enabled=True,
            custom_domain=False,
            priority_support=False,
            api_access=False,
            team_members=1,
            watermark_removal=True
        ),
        description="Perfect for photography enthusiasts"
    ),
    SubscriptionTier.PROFESSIONAL: SubscriptionPlan(
        tier=SubscriptionTier.PROFESSIONAL,
        name="Professional",
        price_monthly=29.0,
        price_yearly=290.0,
        features=SubscriptionFeatures(
            monthly_uploads=-1,  # unlimited
            storage_gb=100.0,
            collections_enabled=True,
            analytics_enabled=True,
            custom_domain=True,
            priority_support=True,
            api_access=True,
            team_members=1,
            watermark_removal=True
        ),
        description="For professional photographers"
    ),
    SubscriptionTier.STUDIO: SubscriptionPlan(
        tier=SubscriptionTier.STUDIO,
        name="Studio",
        price_monthly=99.0,
        price_yearly=990.0,
        features=SubscriptionFeatures(
            monthly_uploads=-1,  # unlimited
            storage_gb=500.0,
            collections_enabled=True,
            analytics_enabled=True,
            custom_domain=True,
            priority_support=True,
            api_access=True,
            team_members=5,
            watermark_removal=True
        ),
        description="For photography studios and teams"
    )
}