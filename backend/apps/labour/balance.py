from datetime import date
from decimal import Decimal

from django.db.models import Sum


def labour_earned_total(labour, as_of: date | None = None) -> Decimal:
    qs = labour.attendances.filter(present=True)
    if as_of is not None:
        qs = qs.filter(date__lte=as_of)
    total = qs.aggregate(s=Sum("wage_rate")).get("s") or Decimal("0")
    return Decimal(total)


def labour_paid_total(labour, as_of: date | None = None) -> Decimal:
    qs = labour.payments.all()
    if as_of is not None:
        qs = qs.filter(payment_date__lte=as_of)
    total = qs.aggregate(s=Sum("amount_paid")).get("s") or Decimal("0")
    return Decimal(total)


def labour_pending_wage(labour, as_of: date | None = None) -> Decimal:
    """Outstanding balance: all earned (present days) minus all payments, optionally capped at a date."""
    return labour_earned_total(labour, as_of) - labour_paid_total(labour, as_of)


def site_pending_as_of(site, as_of: date) -> Decimal:
    """Sum of each worker's outstanding balance on this site through `as_of` (carries forward day to day)."""
    from apps.labour.models import Labour

    total = Decimal("0")
    for labour in Labour.objects.filter(site_id=site.pk, company_id=site.company_id):
        total += labour_pending_wage(labour, as_of)
    return total
