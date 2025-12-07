"""Subscription management endpoints for Lumen API"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Dict, Any

from ...auth_middleware import get_current_user, AuthUser
from ...models.subscription import (
    SubscriptionTier, SubscriptionPlan, CreateCheckoutSessionRequest,
    SUBSCRIPTION_PLANS
)
from ...services.stripe_service import StripeService
from ...services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()
stripe_service = StripeService()
user_service = UserService()

@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """Get all available subscription plans"""
    return list(SUBSCRIPTION_PLANS.values())

@router.get("/plans/{tier}", response_model=SubscriptionPlan)
async def get_subscription_plan(tier: SubscriptionTier):
    """Get details for a specific subscription plan"""
    if tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    return SUBSCRIPTION_PLANS[tier]

@router.post("/checkout")
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    user_token: dict = Depends(get_current_user)
):
    """Create a Stripe checkout session for subscription"""
    firebase_user = AuthUser(user_token)

    try:
        # Get user profile for customer creation
        profile = await user_service.get_or_create_user_profile(firebase_user, include_private=True)

        # Create or get Stripe customer
        customer_id = profile.stripe_customer_id
        if not customer_id:
            customer_id = await stripe_service.create_customer(
                user_id=firebase_user.uid,
                email=firebase_user.email,
                name=profile.display_name or firebase_user.email
            )
            # TODO: Save customer_id to user profile in database

        # Create checkout session
        session_data = await stripe_service.create_checkout_session(
            request=request,
            customer_id=customer_id,
            user_id=firebase_user.uid
        )

        return session_data

    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )

@router.post("/portal")
async def create_customer_portal_session(
    return_url: str,
    user_token: dict = Depends(get_current_user)
):
    """Create a Stripe customer portal session"""
    firebase_user = AuthUser(user_token)

    try:
        # Get user profile
        profile = await user_service.get_or_create_user_profile(firebase_user, include_private=True)

        if not profile.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        portal_url = await stripe_service.get_customer_portal_url(
            customer_id=profile.stripe_customer_id,
            return_url=return_url
        )

        return {"portal_url": portal_url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create customer portal session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer portal session"
        )

@router.get("/current")
async def get_current_subscription(user_token: dict = Depends(get_current_user)):
    """Get current user's subscription details"""
    firebase_user = AuthUser(user_token)

    try:
        # Get user profile
        profile = await user_service.get_or_create_user_profile(firebase_user, include_private=True)

        # Default to free tier if no subscription
        current_tier = getattr(profile, 'subscription_tier', SubscriptionTier.FREE)
        current_plan = SUBSCRIPTION_PLANS[current_tier]

        subscription_data = {
            "tier": current_tier,
            "plan": current_plan,
            "status": "active" if current_tier != SubscriptionTier.FREE else "free",
            "customer_id": getattr(profile, 'stripe_customer_id', None),
            "subscription_id": getattr(profile, 'stripe_subscription_id', None)
        }

        # If user has a Stripe subscription, get details
        if hasattr(profile, 'stripe_subscription_id') and profile.stripe_subscription_id:
            stripe_details = await stripe_service.get_subscription_details(profile.stripe_subscription_id)
            if stripe_details:
                subscription_data.update(stripe_details)

        return subscription_data

    except Exception as e:
        logger.error(f"Failed to get current subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription details"
        )

@router.post("/cancel")
async def cancel_subscription(user_token: dict = Depends(get_current_user)):
    """Cancel current subscription at period end"""
    firebase_user = AuthUser(user_token)

    try:
        # Get user profile
        profile = await user_service.get_or_create_user_profile(firebase_user, include_private=True)

        if not hasattr(profile, 'stripe_subscription_id') or not profile.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription to cancel"
            )

        success = await stripe_service.cancel_subscription(profile.stripe_subscription_id)

        if success:
            return {"message": "Subscription will be cancelled at the end of the billing period"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel subscription"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.post("/reactivate")
async def reactivate_subscription(user_token: dict = Depends(get_current_user)):
    """Reactivate a cancelled subscription"""
    firebase_user = AuthUser(user_token)

    try:
        # Get user profile
        profile = await user_service.get_or_create_user_profile(firebase_user, include_private=True)

        if not hasattr(profile, 'stripe_subscription_id') or not profile.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription to reactivate"
            )

        success = await stripe_service.reactivate_subscription(profile.stripe_subscription_id)

        if success:
            return {"message": "Subscription has been reactivated"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reactivate subscription"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reactivate subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate subscription"
        )

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        signature = request.headers.get('stripe-signature')

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )

        # Verify webhook signature
        if not stripe_service.verify_webhook_signature(payload, signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )

        # Parse webhook event
        import json
        event = json.loads(payload)

        # Handle the event
        success = await stripe_service.handle_webhook_event(
            event_type=event['type'],
            data=event['data']['object']
        )

        if success:
            return {"status": "success"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process webhook"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )