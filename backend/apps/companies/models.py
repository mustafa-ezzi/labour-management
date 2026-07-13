import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_companies",
    )
    # Legacy mirror of active plan key; Subscription is source of truth from Phase 3.
    subscription_plan = models.CharField(max_length=64, default="free")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "companies_company"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CompanyRole(models.TextChoices):
    OWNER = "owner", "Owner"
    MANAGER = "manager", "Manager"
    SUPERVISOR = "supervisor", "Supervisor"
    ACCOUNTANT = "accountant", "Accountant"


class CompanyMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_memberships",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=32,
        choices=CompanyRole.choices,
        default=CompanyRole.OWNER,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "companies_membership"
        unique_together = [["user", "company"]]


class Plan(models.Model):
    """Billing plan catalog (trial / monthly / yearly). No in-app checkout in v1."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    currency = models.CharField(max_length=8, default="PKR")
    duration_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    features = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "companies_plan"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.key})"


class SubscriptionStatus(models.TextChoices):
    TRIALING = "trialing", "Trialing"
    ACTIVE = "active", "Active"
    PAST_DUE = "past_due", "Past due"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


class Subscription(models.Model):
    """One subscription per company. Expiry never auto-disables login (alerts only)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    status = models.CharField(
        max_length=32,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIALING,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    renewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies_subscription"
        ordering = ["ends_at"]

    def __str__(self):
        return f"{self.company_id} · {self.status} · {self.ends_at.date()}"
