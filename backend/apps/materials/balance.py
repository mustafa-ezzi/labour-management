from datetime import date
from decimal import Decimal

from django.db.models import Sum


def material_usage_cost_total(material, as_of: date | None = None) -> Decimal:
    """Sum of logged usage amounts (the bill)."""
    qs = material.usage_entries.all()
    if as_of is not None:
        qs = qs.filter(usage_date__lte=as_of)
    total = qs.aggregate(s=Sum("calculated_amount")).get("s") or Decimal("0")
    return Decimal(total)


def material_paid_total(material, as_of: date | None = None) -> Decimal:
    qs = material.payments.all()
    if as_of is not None:
        qs = qs.filter(payment_date__lte=as_of)
    total = qs.aggregate(s=Sum("amount_paid")).get("s") or Decimal("0")
    return Decimal(total)


def material_pending_amount(material, as_of: date | None = None) -> Decimal:
    """Outstanding: total usage cost minus all payments on this material."""
    return material_usage_cost_total(material, as_of) - material_paid_total(material, as_of)


def usage_paid_total(usage, as_of: date | None = None) -> Decimal:
    qs = usage.payments.all()
    if as_of is not None:
        qs = qs.filter(payment_date__lte=as_of)
    total = qs.aggregate(s=Sum("amount_paid")).get("s") or Decimal("0")
    return Decimal(total)


def usage_pending_amount(usage, as_of: date | None = None) -> Decimal:
    """Outstanding on a single usage log (payments linked to that log only)."""
    return Decimal(usage.calculated_amount) - usage_paid_total(usage, as_of)


def site_material_pending_as_of(site, as_of: date) -> Decimal:
    from .models import Material

    total = Decimal("0")
    for material in Material.objects.filter(site_id=site.pk, company_id=site.company_id):
        total += material_pending_amount(material, as_of)
    return total
