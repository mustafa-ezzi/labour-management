import uuid

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
