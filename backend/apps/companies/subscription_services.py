"""Subscription lifecycle helpers — expiry is status-only; never disables login."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.companies.models import (
    Company,
    Plan,
    Subscription,
    SubscriptionStatus,
)

DEFAULT_PLANS = (
    {
        "key": "trial",
        "name": "Free trial",
        "price": Decimal("0"),
        "currency": "PKR",
        "duration_days": 14,
        "sort_order": 0,
        "features": {"description": "14-day free trial for new workspaces"},
    },
    {
        "key": "monthly",
        "name": "Monthly",
        "price": Decimal("0"),
        "currency": "PKR",
        "duration_days": 30,
        "sort_order": 1,
        "features": {"description": "Default paid plan (price set by Admin)"},
    },
    {
        "key": "yearly",
        "name": "Yearly",
        "price": Decimal("0"),
        "currency": "PKR",
        "duration_days": 365,
        "sort_order": 2,
        "features": {"description": "Annual plan (price set by Admin)"},
    },
)


def ensure_default_plans() -> dict[str, Plan]:
    plans: dict[str, Plan] = {}
    for spec in DEFAULT_PLANS:
        plan, _ = Plan.objects.update_or_create(
            key=spec["key"],
            defaults={
                "name": spec["name"],
                "price": spec["price"],
                "currency": spec["currency"],
                "duration_days": spec["duration_days"],
                "sort_order": spec["sort_order"],
                "features": spec["features"],
                "is_active": True,
            },
        )
        plans[plan.key] = plan
    return plans


def serialize_plan(plan: Plan) -> dict:
    return {
        "id": str(plan.id),
        "key": plan.key,
        "name": plan.name,
        "price": str(plan.price),
        "currency": plan.currency,
        "duration_days": plan.duration_days,
        "is_active": plan.is_active,
        "features": plan.features or {},
        "sort_order": plan.sort_order,
    }


def days_remaining(ends_at) -> int:
    if not ends_at:
        return 0
    delta = ends_at - timezone.now()
    return max(0, int(delta.total_seconds() // 86400))


def sync_company_plan_key(company: Company, plan: Plan) -> None:
    if company.subscription_plan != plan.key:
        company.subscription_plan = plan.key
        company.save(update_fields=["subscription_plan"])


def refresh_subscription_status(sub: Subscription, *, save: bool = True) -> Subscription:
    """Mark expired when ends_at has passed. Does not touch User.is_active."""
    if sub.status in (
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.EXPIRED,
    ):
        return sub
    if sub.ends_at <= timezone.now():
        sub.status = SubscriptionStatus.EXPIRED
        if save:
            sub.save(update_fields=["status", "updated_at"])
    return sub


def serialize_subscription(sub: Subscription | None) -> dict | None:
    if not sub:
        return None
    refresh_subscription_status(sub)
    remaining = days_remaining(sub.ends_at)
    ending_soon = (
        sub.status in (SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE)
        and remaining <= 7
    )
    return {
        "id": str(sub.id),
        "company_id": str(sub.company_id),
        "company_name": sub.company.name,
        "status": sub.status,
        "starts_at": sub.starts_at.isoformat(),
        "ends_at": sub.ends_at.isoformat(),
        "renewed_at": sub.renewed_at.isoformat() if sub.renewed_at else None,
        "notes": sub.notes or "",
        "days_remaining": remaining,
        "ending_soon": ending_soon,
        "is_expired": sub.status == SubscriptionStatus.EXPIRED
        or (sub.ends_at <= timezone.now() and sub.status != SubscriptionStatus.CANCELLED),
        "alerts_only": True,
        "plan": serialize_plan(sub.plan),
        "owner_email": sub.company.owner.email if sub.company.owner_id else None,
        "updated_at": sub.updated_at.isoformat() if sub.updated_at else None,
    }


@transaction.atomic
def start_trial_for_company(company: Company) -> Subscription:
    plans = ensure_default_plans()
    plan = plans["trial"]
    now = timezone.now()
    sub, created = Subscription.objects.select_for_update().get_or_create(
        company=company,
        defaults={
            "plan": plan,
            "status": SubscriptionStatus.TRIALING,
            "starts_at": now,
            "ends_at": now + timedelta(days=plan.duration_days),
        },
    )
    if not created:
        return refresh_subscription_status(sub)
    sync_company_plan_key(company, plan)
    return sub


@transaction.atomic
def ensure_subscription_for_company(
    company: Company,
    *,
    plan_key: str = "monthly",
    duration_days: int | None = None,
    status: str = SubscriptionStatus.ACTIVE,
) -> Subscription:
    """Used for backfill of existing companies."""
    plans = ensure_default_plans()
    plan = plans.get(plan_key) or plans["monthly"]
    now = timezone.now()
    days = duration_days if duration_days is not None else plan.duration_days
    sub, created = Subscription.objects.select_for_update().get_or_create(
        company=company,
        defaults={
            "plan": plan,
            "status": status,
            "starts_at": now,
            "ends_at": now + timedelta(days=days),
        },
    )
    if created:
        sync_company_plan_key(company, plan)
    return refresh_subscription_status(sub)


@transaction.atomic
def renew_subscription(
    sub: Subscription,
    *,
    plan: Plan | None = None,
    days: int | None = None,
    notes: str | None = None,
) -> Subscription:
    plan = plan or sub.plan
    duration = days if days is not None else plan.duration_days
    now = timezone.now()
    base = sub.ends_at if sub.ends_at > now else now
    sub.plan = plan
    sub.ends_at = base + timedelta(days=duration)
    sub.renewed_at = now
    sub.status = (
        SubscriptionStatus.TRIALING
        if plan.key == "trial"
        else SubscriptionStatus.ACTIVE
    )
    if notes is not None:
        sub.notes = notes
    sub.save()
    sync_company_plan_key(sub.company, plan)
    return sub


@transaction.atomic
def cancel_subscription(sub: Subscription, *, notes: str | None = None) -> Subscription:
    """Mark cancelled for billing tracking only — does not disable the user."""
    sub.status = SubscriptionStatus.CANCELLED
    if notes is not None:
        sub.notes = notes
    sub.save(update_fields=["status", "notes", "updated_at"])
    return sub


@transaction.atomic
def set_subscription_dates(
    sub: Subscription,
    *,
    starts_at=None,
    ends_at=None,
    status: str | None = None,
    notes: str | None = None,
) -> Subscription:
    if starts_at is not None:
        sub.starts_at = starts_at
    if ends_at is not None:
        sub.ends_at = ends_at
    if status is not None:
        sub.status = status
    if notes is not None:
        sub.notes = notes
    sub.save()
    return refresh_subscription_status(sub)


@transaction.atomic
def change_subscription_plan(sub: Subscription, plan: Plan) -> Subscription:
    sub.plan = plan
    if sub.status not in (SubscriptionStatus.CANCELLED, SubscriptionStatus.EXPIRED):
        sub.status = (
            SubscriptionStatus.TRIALING
            if plan.key == "trial"
            else SubscriptionStatus.ACTIVE
        )
    sub.save()
    sync_company_plan_key(sub.company, plan)
    return refresh_subscription_status(sub)


def mark_expired_subscriptions() -> int:
    """Nightly job: flip active/trialing past ends_at → expired. No account disable."""
    now = timezone.now()
    return (
        Subscription.objects.filter(
            status__in=[
                SubscriptionStatus.TRIALING,
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.PAST_DUE,
            ],
            ends_at__lte=now,
        ).update(status=SubscriptionStatus.EXPIRED)
    )


def company_for_user(user) -> Company | None:
    membership = (
        user.company_memberships.select_related("company").order_by("created_at").first()
    )
    if membership:
        return membership.company
    return user.owned_companies.order_by("created_at").first()
