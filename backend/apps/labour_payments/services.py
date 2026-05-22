from decimal import Decimal

from apps.labour.balance import labour_pending_wage
from apps.labour_payments.models import LabourPayment, PaymentType


def record_labour_payment(labour, amount_paid, payment_date, notes: str = "") -> LabourPayment:
    amount = Decimal(str(amount_paid))
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    pending = labour_pending_wage(labour, payment_date)
    if amount > pending:
        raise ValueError(f"Amount {amount} exceeds outstanding balance ({pending}) as of {payment_date}.")

    remaining = pending - amount
    payment_type = PaymentType.FULL if amount == pending else PaymentType.PARTIAL

    return LabourPayment.objects.create(
        company=labour.company,
        labour=labour,
        amount_paid=amount,
        payment_date=payment_date,
        remaining_amount=remaining,
        payment_type=payment_type,
        notes=notes or "",
    )
