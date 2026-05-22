from django.contrib import admin

from .models import Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "from_date", "to_date", "total_work_days", "created_at")
    list_filter = ("company",)
    search_fields = ("name", "location")
