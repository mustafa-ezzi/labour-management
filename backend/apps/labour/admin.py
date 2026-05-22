from django.contrib import admin

from .models import Labour


@admin.register(Labour)
class LabourAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "site", "daily_wage", "status", "created_at")
    list_filter = ("status", "company")
    search_fields = ("name", "phone_number")
