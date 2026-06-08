import uuid
from django.db import models


class Material(models.Model):
    """
    Master material definition per site.
    Totals are NEVER stored here — always computed from MaterialUsage records.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="materials",
    )
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.CASCADE,
        related_name="materials",
    )
    name = models.CharField(max_length=200)
    unit_of_measure = models.CharField(max_length=50)  # KG, Bags, Liters, m³, etc.
    rate_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "materials_material"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.unit_of_measure}) @ {self.rate_per_unit}"

    def save(self, *args, **kwargs):
        # Inherit company from site if not set
        if self.site_id and not self.company_id:
            self.company_id = self.site.company_id
        super().save(*args, **kwargs)


class MaterialUsage(models.Model):
    """
    Daily consumption entry for a material.
    calculated_amount is always derived from quantity_used × rate_per_unit at time of entry.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="usage_entries",
    )
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.CASCADE,
        related_name="material_usage",
    )
    usage_date = models.DateField()
    quantity_used = models.DecimalField(max_digits=14, decimal_places=3)
    calculated_amount = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        editable=False,
        help_text="Auto-calculated: quantity_used × rate_per_unit at time of entry",
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "materials_usage"
        ordering = ["-usage_date", "-created_at"]

    def __str__(self):
        uom = self.material.unit_of_measure
        return (
            f"{self.material.name} — {self.usage_date}: "
            f"{self.quantity_used} {uom} = {self.calculated_amount}"
        )

    def save(self, *args, **kwargs):
        # Always recalculate on every save — prevents drift if rate is updated
        self.calculated_amount = self.material.rate_per_unit * self.quantity_used
        # Sync site from material to avoid mismatch
        self.site_id = self.material.site_id
        super().save(*args, **kwargs)


class MaterialPaymentType(models.TextChoices):
    FULL = "full", "Full"
    PARTIAL = "partial", "Partial"


class MaterialPayment(models.Model):
    """
    Payment against material usage costs.
    - material_usage set: allocated to a specific daily log (for line-item reports).
    - material_usage null: general payment reducing site/material balance.
    Denormalized company/site support future report filters without deep joins.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="material_payments",
    )
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.CASCADE,
        related_name="material_payments",
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    material_usage = models.ForeignKey(
        MaterialUsage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    payment_type = models.CharField(
        max_length=16,
        choices=MaterialPaymentType.choices,
        default=MaterialPaymentType.PARTIAL,
    )
    amount_paid = models.DecimalField(max_digits=16, decimal_places=2)
    payment_date = models.DateField()
    remaining_amount = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        help_text="Material outstanding balance immediately after this payment.",
    )
    notes = models.CharField(max_length=512, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "materials_payment"
        ordering = ["-payment_date", "-created_at"]
        indexes = [
            models.Index(fields=["company", "payment_date"], name="matpay_co_date_idx"),
            models.Index(fields=["site", "payment_date"], name="matpay_site_date_idx"),
            models.Index(fields=["material", "payment_date"], name="matpay_mat_date_idx"),
        ]

    def __str__(self):
        target = f"usage {self.material_usage_id}" if self.material_usage_id else self.material.name
        return f"{target} {self.amount_paid} on {self.payment_date}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.material_id and self.company_id and self.material.company_id != self.company_id:
            raise ValidationError({"material": "Material must belong to the same company."})
        if self.site_id and self.material_id and self.material.site_id != self.site_id:
            raise ValidationError({"site": "Site must match the material's site."})
        if self.material_usage_id and self.material_id:
            if self.material_usage.material_id != self.material_id:
                raise ValidationError(
                    {"material_usage": "Usage entry must belong to the same material."}
                )

    def save(self, *args, **kwargs):
        if self.material_id:
            if not self.company_id:
                self.company_id = self.material.company_id
            if not self.site_id:
                self.site_id = self.material.site_id
        self.full_clean()
        super().save(*args, **kwargs)
