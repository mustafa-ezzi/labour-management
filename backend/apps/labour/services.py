from datetime import date
from decimal import Decimal

from apps.attendance.models import Attendance
from apps.labour.balance import labour_pending_wage
from apps.labour_payments.models import LabourPayment, PaymentType


def record_daily_wage_entry(
    labour,
    entry_date: date,
    wage_amount: Decimal,
    amount_paid: Decimal,
    notes: str = "",
):
    """Combined "Daily Wages" entry: one row per worker per day.

    Entering a wage > 0 marks the worker present for the day (wage snapshot =
    wage_amount). The amount paid for that same day is reconciled as a single
    LabourPayment linked to that attendance record, so re-saving the same day
    (e.g. editing the paid amount later) updates it in place instead of
    stacking duplicate payments.

    Returns (attendance, payment_or_None, pending_wage_after).
    """
    wage_amount = Decimal(str(wage_amount or 0))
    amount_paid = Decimal(str(amount_paid or 0))
    present = wage_amount > 0

    attendance, _ = Attendance.objects.update_or_create(
        labour=labour,
        date=entry_date,
        defaults={
            "company": labour.company,
            "site": labour.site,
            "present": present,
            "wage_rate": wage_amount if present else Decimal("0"),
            "notes": notes or "",
        },
    )

    existing_payment = LabourPayment.objects.filter(labour=labour, attendance=attendance).first()

    if amount_paid <= 0:
        if existing_payment:
            existing_payment.delete()
        return attendance, None, labour_pending_wage(labour, entry_date)

    pending_before = labour_pending_wage(labour, entry_date)
    if existing_payment:
        # Exclude the payment we're about to replace from the baseline.
        pending_before += existing_payment.amount_paid

    if amount_paid > pending_before:
        raise ValueError(
            f"Amount {amount_paid} exceeds outstanding balance ({pending_before}) as of {entry_date}."
        )

    remaining = pending_before - amount_paid
    payment_type = PaymentType.FULL if amount_paid == pending_before else PaymentType.PARTIAL

    if existing_payment:
        existing_payment.amount_paid = amount_paid
        existing_payment.payment_date = entry_date
        existing_payment.remaining_amount = remaining
        existing_payment.payment_type = payment_type
        existing_payment.notes = notes or existing_payment.notes
        existing_payment.full_clean()
        existing_payment.save()
        payment = existing_payment
    else:
        payment = LabourPayment.objects.create(
            company=labour.company,
            labour=labour,
            attendance=attendance,
            amount_paid=amount_paid,
            payment_date=entry_date,
            remaining_amount=remaining,
            payment_type=payment_type,
            notes=notes or "",
        )

    return attendance, payment, remaining
