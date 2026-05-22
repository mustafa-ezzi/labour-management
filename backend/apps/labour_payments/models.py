import uuid

from django.core.exceptions import ValidationError
from django.db import models


class PaymentType(models.TextChoices):
    FULL = "full", "Full"
    PARTIAL = "partial", "Partial"


class LabourPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="labour_payments",
    )
    labour = models.ForeignKey(
        "labour.Labour",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    attendance = models.ForeignKey(
        "attendance.Attendance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    payment_type = models.CharField(
        max_length=16,
        choices=PaymentType.choices,
        default=PaymentType.PARTIAL,
    )
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Outstanding wage balance immediately after this payment.",
    )
    notes = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "labour_payments_labourpayment"
        ordering = ["-payment_date", "-created_at"]

    def __str__(self):
        return f"{self.labour} {self.amount_paid} on {self.payment_date}"

    def clean(self):
        if self.labour_id and self.company_id and self.labour.company_id != self.company_id:
            raise ValidationError({"labour": "Labour must belong to the same company."})
        if self.attendance_id and self.labour_id:
            if self.attendance.labour_id != self.labour_id:
                raise ValidationError({"attendance": "Attendance must belong to the same labour."})

    def save(self, *args, **kwargs):
        if self.labour_id and not self.company_id:
            self.company_id = self.labour.company_id
        self.full_clean()
        super().save(*args, **kwargs)
