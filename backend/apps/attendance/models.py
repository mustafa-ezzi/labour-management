import uuid

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    labour = models.ForeignKey(
        "labour.Labour",
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    date = models.DateField()
    present = models.BooleanField(default=True)
    overtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    wage_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Snapshot of daily wage when attendance was recorded.",
    )
    notes = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_attendance"
        ordering = ["-date", "labour__name"]
        constraints = [
            models.UniqueConstraint(fields=["labour", "date"], name="uniq_attendance_labour_date"),
        ]

    def __str__(self):
        return f"{self.labour} {self.date}"

    def clean(self):
        if self.labour_id and self.site_id and self.labour.site_id != self.site_id:
            raise ValidationError({"site": "Site must match the labour's site."})
        if self.labour_id and self.company_id and self.labour.company_id != self.company_id:
            raise ValidationError({"company": "Company must match the labour's company."})

    def save(self, *args, **kwargs):
        if self.labour_id:
            if not self.company_id:
                self.company_id = self.labour.company_id
            if not self.site_id:
                self.site_id = self.labour.site_id
            if not self.present:
                self.wage_rate = Decimal("0")
            elif not self.wage_rate:
                # Explicit "wage of the day" values are preserved; only default
                # to the worker's standard rate when none was supplied.
                self.wage_rate = self.labour.daily_wage
        self.full_clean()
        super().save(*args, **kwargs)
