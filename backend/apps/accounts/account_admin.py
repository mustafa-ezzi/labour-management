"""Hard-delete a customer user and all workspace data they own."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.companies.models import Company, CompanyMembership
from apps.labour.models import Labour
from apps.materials.models import Material
from apps.sites.models import Site

User = get_user_model()


class AccountDeleteError(Exception):
    pass


def account_usage_counts(user) -> dict:
    company_ids = list(
        Company.objects.filter(owner=user).values_list("id", flat=True)
    ) + list(
        user.company_memberships.values_list("company_id", flat=True)
    )
    company_ids = list(dict.fromkeys(company_ids))
    return {
        "companies": len(company_ids),
        "sites": Site.objects.filter(company_id__in=company_ids).count() if company_ids else 0,
        "workers": Labour.objects.filter(company_id__in=company_ids).count() if company_ids else 0,
        "materials": Material.objects.filter(company_id__in=company_ids).count() if company_ids else 0,
    }


def serialize_account(user) -> dict:
    membership = (
        user.company_memberships.select_related("company").order_by("created_at").first()
    )
    company = None
    if membership:
        c = membership.company
        counts = account_usage_counts(user)
        company = {
            "id": str(c.id),
            "name": c.name,
            "subscription_plan": c.subscription_plan,
            "role": membership.role,
            "created_at": c.created_at.isoformat(),
        }
    elif user.owned_companies.exists():
        c = user.owned_companies.order_by("created_at").first()
        counts = account_usage_counts(user)
        company = {
            "id": str(c.id),
            "name": c.name,
            "subscription_plan": c.subscription_plan,
            "role": "owner",
            "created_at": c.created_at.isoformat(),
        }
    else:
        counts = {"companies": 0, "sites": 0, "workers": 0, "materials": 0}

    status = "active" if user.is_active else "disabled"
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "status": status,
        "is_app_admin": bool(user.is_superuser),
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "company": company,
        "counts": counts,
        "subscription_plan": company["subscription_plan"] if company else "none",
    }


@transaction.atomic
def hard_delete_account(*, target_user, actor) -> dict:
    """
    Delete owned companies (CASCADE site/crew/materials/payments), then the user.
    Company.owner is PROTECT — companies must be deleted before the user.
    """
    if target_user.is_superuser:
        raise AccountDeleteError("Cannot delete the App Admin account.")
    if actor and str(actor.pk) == str(target_user.pk):
        raise AccountDeleteError("Cannot delete your own account.")

    owned = list(Company.objects.filter(owner=target_user))
    summary = {
        "email": target_user.email,
        "companies_deleted": len(owned),
        "user_id": str(target_user.pk),
    }

    # Remove memberships on companies this user does not own
    CompanyMembership.objects.filter(user=target_user).exclude(
        company__owner=target_user
    ).delete()

    for company in owned:
        company.delete()

    target_user.delete()
    return summary
