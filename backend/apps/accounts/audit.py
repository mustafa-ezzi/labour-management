import uuid

from django.conf import settings
from django.db import models


class AdminAuditLog(models.Model):
    """Immutable record of App Admin actions (disable, delete, renew, support reply, …)."""

    class Action(models.TextChoices):
        LOGIN = "login", "Admin login"
        DISABLE_USER = "disable_user", "Disable user"
        ENABLE_USER = "enable_user", "Enable user"
        UPDATE_USER = "update_user", "Update user"
        DELETE_USER = "delete_user", "Delete user"
        RENEW_SUBSCRIPTION = "renew_subscription", "Renew subscription"
        DISABLE_SUBSCRIPTION = "disable_subscription", "Disable subscription"
        UPDATE_SUBSCRIPTION = "update_subscription", "Update subscription"
        SUPPORT_REPLY = "support_reply", "Support reply"
        SUPPORT_STATUS = "support_status", "Support status change"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_audit_actions",
    )
    action = models.CharField(max_length=64, choices=Action.choices)
    target_type = models.CharField(max_length=64, blank=True, default="")
    target_id = models.CharField(max_length=64, blank=True, default="")
    summary = models.CharField(max_length=512, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_admin_audit_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} by {self.actor_id} at {self.created_at}"
