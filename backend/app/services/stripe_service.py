"""Stripe payment processing service"""

import os
import stripe
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.subscription import (
    SubscriptionTier, SubscriptionStatus, UserSubscription,
    CreateCheckoutSessionRequest, SUBSCRIPTION_PLANS
)

logger = logging.getLogger(__name__)

class StripeService:
    """Service for handling Stripe payment operations"""

    def __init__(self):
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

        if not self.stripe_secret_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")

        stripe.api_key = self.stripe_secret_key

        # Product and price IDs (these will be created in Stripe dashboard)
        self.price_ids = {
            'hobbyist_monthly': 'price_hobbyist_monthly',
            'hobbyist_yearly': 'price_hobbyist_yearly',
            'professional_monthly': 'price_professional_monthly',
            'professional_yearly': 'price_professional_yearly',
            'studio_monthly': 'price_studio_monthly',
            'studio_yearly': 'price_studio_yearly'
        }

    async def create_customer(self, user_id: str, email: str, name: str) -> str:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={'user_id': user_id}
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    async def create_checkout_session(
        self,
        request: CreateCheckoutSessionRequest,
        customer_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Create a Stripe checkout session"""
        try:
            plan = SUBSCRIPTION_PLANS[request.tier]

            # Determine price based on billing cycle
            if request.billing_cycle == "yearly":
                price = plan.price_yearly
                price_id = getattr(plan, 'stripe_price_id_yearly', None)
            else:
                price = plan.price_monthly
                price_id = getattr(plan, 'stripe_price_id_monthly', None)

            if not price_id:
                # Fallback to creating price on the fly for development
                price_id = await self._create_price_on_demand(request.tier, request.billing_cycle, price)

            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.success_url,
                cancel_url=request.cancel_url,
                metadata={
                    'user_id': user_id,
                    'tier': request.tier.value,
                    'billing_cycle': request.billing_cycle
                }
            )

            return {
                'checkout_url': session.url,
                'session_id': session.id
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    async def _create_price_on_demand(self, tier: SubscriptionTier, billing_cycle: str, amount: float) -> str:
        """Create a Stripe price on demand for development/testing"""
        try:
            plan = SUBSCRIPTION_PLANS[tier]

            # Create product if it doesn't exist
            product = stripe.Product.create(
                name=f"Lumen {plan.name}",
                description=plan.description,
                metadata={'tier': tier.value}
            )

            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(amount * 100),  # Convert to cents
                currency='usd',
                recurring={
                    'interval': 'month' if billing_cycle == 'monthly' else 'year'
                },
                metadata={
                    'tier': tier.value,
                    'billing_cycle': billing_cycle
                }
            )

            logger.info(f"Created price {price.id} for {tier.value} {billing_cycle}")
            return price.id

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create price on demand: {e}")
            raise

    async def get_customer_portal_url(self, customer_id: str, return_url: str) -> str:
        """Create a customer portal session"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create customer portal session: {e}")
            raise

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription at period end"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return subscription.cancel_at_period_end
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    async def reactivate_subscription(self, subscription_id: str) -> bool:
        """Reactivate a cancelled subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
            return not subscription.cancel_at_period_end
        except stripe.error.StripeError as e:
            logger.error(f"Failed to reactivate subscription: {e}")
            raise

    async def get_subscription_details(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'trial_end': datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription details: {e}")
            return None

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return False
        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return False

    async def handle_webhook_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Handle incoming Stripe webhook events"""
        try:
            if event_type == 'customer.subscription.created':
                await self._handle_subscription_created(data)
            elif event_type == 'customer.subscription.updated':
                await self._handle_subscription_updated(data)
            elif event_type == 'customer.subscription.deleted':
                await self._handle_subscription_deleted(data)
            elif event_type == 'invoice.payment_succeeded':
                await self._handle_payment_succeeded(data)
            elif event_type == 'invoice.payment_failed':
                await self._handle_payment_failed(data)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")

            return True

        except Exception as e:
            logger.error(f"Failed to handle webhook event {event_type}: {e}")
            return False

    async def _handle_subscription_created(self, data: Dict[str, Any]):
        """Handle subscription created webhook"""
        # TODO: Update user subscription in database
        logger.info(f"Subscription created: {data.get('id')}")

    async def _handle_subscription_updated(self, data: Dict[str, Any]):
        """Handle subscription updated webhook"""
        # TODO: Update user subscription in database
        logger.info(f"Subscription updated: {data.get('id')}")

    async def _handle_subscription_deleted(self, data: Dict[str, Any]):
        """Handle subscription deleted webhook"""
        # TODO: Update user subscription in database
        logger.info(f"Subscription deleted: {data.get('id')}")

    async def _handle_payment_succeeded(self, data: Dict[str, Any]):
        """Handle payment succeeded webhook"""
        logger.info(f"Payment succeeded for subscription: {data.get('subscription')}")

    async def _handle_payment_failed(self, data: Dict[str, Any]):
        """Handle payment failed webhook"""
        logger.error(f"Payment failed for subscription: {data.get('subscription')}")