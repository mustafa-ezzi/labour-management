from decimal import Decimal

from .balance import material_pending_amount, usage_pending_amount
from .models import MaterialPayment, MaterialPaymentType


def record_material_payment(
    material,
    amount_paid,
    payment_date,
    notes: str = "",
    material_usage=None,
) -> MaterialPayment:
    amount = Decimal(str(amount_paid))
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    pending = material_pending_amount(material, payment_date)
    if amount > pending:
        raise ValueError(
            f"Amount {amount} exceeds outstanding balance ({pending}) as of {payment_date}."
        )

    if material_usage is not None:
        if material_usage.material_id != material.pk:
            raise ValueError("Usage entry does not belong to this material.")
        usage_pending = usage_pending_amount(material_usage, payment_date)
        if amount > usage_pending:
            raise ValueError(
                f"Amount {amount} exceeds this log's outstanding ({usage_pending})."
            )

    remaining = pending - amount
    payment_type = MaterialPaymentType.FULL if amount == pending else MaterialPaymentType.PARTIAL

    return MaterialPayment.objects.create(
        company=material.company,
        site=material.site,
        material=material,
        material_usage=material_usage,
        amount_paid=amount,
        payment_date=payment_date,
        remaining_amount=remaining,
        payment_type=payment_type,
        notes=notes or "",
    )
