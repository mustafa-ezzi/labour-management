from django.contrib import admin
from .models import Material, MaterialPayment, MaterialUsage


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["name", "site", "unit_of_measure", "rate_per_unit", "created_at"]
    list_filter = ["site__company", "unit_of_measure"]
    search_fields = ["name", "site__name"]


@admin.register(MaterialUsage)
class MaterialUsageAdmin(admin.ModelAdmin):
    list_display = ["material", "usage_date", "quantity_used", "calculated_amount", "notes"]
    list_filter = ["usage_date", "material__site"]
    search_fields = ["material__name"]
    readonly_fields = ["calculated_amount", "site"]


@admin.register(MaterialPayment)
class MaterialPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "material",
        "amount_paid",
        "payment_date",
        "payment_type",
        "material_usage",
        "site",
        "created_at",
    ]
    list_filter = ["payment_date", "payment_type", "site__company"]
    search_fields = ["material__name", "notes"]
    readonly_fields = ["company", "site", "remaining_amount", "payment_type"]
