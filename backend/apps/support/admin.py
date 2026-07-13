from django.contrib import admin

from .models import SupportMessage, SupportTicket


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ("sender", "body", "is_admin_reply", "created_at")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "company",
        "status",
        "priority",
        "admin_unread",
        "user_unread",
        "updated_at",
    )
    list_filter = ("status", "priority", "admin_unread")
    search_fields = ("subject", "company__name", "created_by__email")
    inlines = [SupportMessageInline]


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "sender", "is_admin_reply", "created_at")
    list_filter = ("is_admin_reply",)
