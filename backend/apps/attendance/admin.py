from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("labour", "site", "date", "present", "wage_rate", "created_at")
    list_filter = ("present", "company", "site")
    date_hierarchy = "date"
