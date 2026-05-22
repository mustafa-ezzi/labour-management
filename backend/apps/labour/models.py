import uuid

from django.core.exceptions import ValidationError
from django.db import models


class LabourStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class Labour(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="labours",
    )
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.CASCADE,
        related_name="labours",
    )
    name = models.CharField(max_length=255)
    daily_wage = models.DecimalField(max_digits=12, decimal_places=2)
    phone_number = models.CharField(max_length=32, blank=True)
    status = models.CharField(
        max_length=16,
        choices=LabourStatus.choices,
        default=LabourStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "labour_labour"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        if self.site_id and self.company_id and self.site.company_id != self.company_id:
            raise ValidationError({"site": "Site must belong to the same company as the labour record."})

    def save(self, *args, **kwargs):
        if self.site_id and not self.company_id:
            self.company_id = self.site.company_id
        self.full_clean()
        super().save(*args, **kwargs)
