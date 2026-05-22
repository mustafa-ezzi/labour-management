import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="sites",
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=512, blank=True)
    from_date = models.DateField()
    to_date = models.DateField()
    total_work_days = models.PositiveIntegerField(default=0, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sites_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sites_site"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def clean(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValidationError({"to_date": "End date cannot be before start date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.from_date and self.to_date:
            delta = (self.to_date - self.from_date).days + 1
            self.total_work_days = max(0, delta)
        super().save(*args, **kwargs)
