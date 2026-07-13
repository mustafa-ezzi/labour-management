from django.contrib import admin

from .models import Company, CompanyMembership, Plan, Subscription


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "subscription_plan", "created_at")
    search_fields = ("name",)


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "created_at")
    list_filter = ("role",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "price", "currency", "duration_days", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "key")
    prepopulated_fields = {"key": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("company", "plan", "status", "starts_at", "ends_at", "renewed_at")
    list_filter = ("status", "plan")
    search_fields = ("company__name", "company__owner__email")
    raw_id_fields = ("company", "plan")
