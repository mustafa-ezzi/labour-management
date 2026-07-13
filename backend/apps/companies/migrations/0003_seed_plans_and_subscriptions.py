"""Seed default plans and attach subscriptions to existing companies."""

from datetime import timedelta
from decimal import Decimal

from django.db import migrations
from django.utils import timezone


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


def seed_plans_and_subscriptions(apps, schema_editor):
    Plan = apps.get_model("companies", "Plan")
    Company = apps.get_model("companies", "Company")
    Subscription = apps.get_model("companies", "Subscription")

    plans = {}
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

    monthly = plans["monthly"]
    now = timezone.now()
    for company in Company.objects.all():
        if Subscription.objects.filter(company_id=company.id).exists():
            continue
        Subscription.objects.create(
            company=company,
            plan=monthly,
            status="active",
            starts_at=now,
            ends_at=now + timedelta(days=30),
        )
        if company.subscription_plan != "monthly":
            company.subscription_plan = "monthly"
            company.save(update_fields=["subscription_plan"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0002_plan_and_subscription"),
    ]

    operations = [
        migrations.RunPython(seed_plans_and_subscriptions, noop_reverse),
    ]
