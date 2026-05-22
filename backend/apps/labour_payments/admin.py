from django.contrib import admin

from .models import LabourPayment


@admin.register(LabourPayment)
class LabourPaymentAdmin(admin.ModelAdmin):
    list_display = ("labour", "amount_paid", "payment_date", "payment_type", "remaining_amount", "created_at")
    list_filter = ("company", "payment_type")
