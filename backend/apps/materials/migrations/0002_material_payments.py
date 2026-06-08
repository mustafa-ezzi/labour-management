# Generated manually for material payments

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0001_initial"),
        ("materials", "0001_initial"),
        ("sites", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MaterialPayment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "payment_type",
                    models.CharField(
                        choices=[("full", "Full"), ("partial", "Partial")],
                        default="partial",
                        max_length=16,
                    ),
                ),
                ("amount_paid", models.DecimalField(decimal_places=2, max_digits=16)),
                ("payment_date", models.DateField()),
                (
                    "remaining_amount",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Material outstanding balance immediately after this payment.",
                        max_digits=16,
                    ),
                ),
                ("notes", models.CharField(blank=True, default="", max_length=512)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="material_payments",
                        to="companies.company",
                    ),
                ),
                (
                    "material",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="materials.material",
                    ),
                ),
                (
                    "material_usage",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payments",
                        to="materials.materialusage",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="material_payments",
                        to="sites.site",
                    ),
                ),
            ],
            options={
                "db_table": "materials_payment",
                "ordering": ["-payment_date", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="materialpayment",
            index=models.Index(fields=["company", "payment_date"], name="matpay_co_date_idx"),
        ),
        migrations.AddIndex(
            model_name="materialpayment",
            index=models.Index(fields=["site", "payment_date"], name="matpay_site_date_idx"),
        ),
        migrations.AddIndex(
            model_name="materialpayment",
            index=models.Index(fields=["material", "payment_date"], name="matpay_mat_date_idx"),
        ),
    ]
