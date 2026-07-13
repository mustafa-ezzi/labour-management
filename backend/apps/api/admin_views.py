"""App Admin API — Phase 1: access control, me, dashboard stub, audit list."""

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.audit import AdminAuditLog
from apps.api.permissions import IsAppAdmin
from apps.companies.models import Company

User = get_user_model()


class AdminMeView(APIView):
    """Confirm App Admin identity (no company membership required)."""

    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        return Response(
            {
                "user": {
                    "id": str(request.user.id),
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "is_app_admin": True,
                }
            }
        )


class AdminDashboardView(APIView):
    """Lightweight KPIs for admin home (Phase 1 shell; expand in Phase 5)."""

    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        users = User.objects.filter(is_superuser=False)
        return Response(
            {
                "total_users": users.count(),
                "active_users": users.filter(is_active=True).count(),
                "disabled_users": users.filter(is_active=False).count(),
                "total_companies": Company.objects.count(),
                "open_support_tickets": 0,  # Phase 4
                "active_subscriptions": 0,  # Phase 3
                "expired_subscriptions": 0,  # Phase 3
                "phase": "1",
                "note": "Accounts, subscriptions, and support land in later phases.",
            }
        )


class AdminAuditListView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        qs = AdminAuditLog.objects.select_related("actor")[:100]
        results = [
            {
                "id": str(row.id),
                "action": row.action,
                "summary": row.summary,
                "target_type": row.target_type,
                "target_id": row.target_id,
                "metadata": row.metadata,
                "created_at": row.created_at.isoformat(),
                "actor_email": row.actor.email if row.actor else None,
            }
            for row in qs
        ]
        return Response({"results": results})


class AdminGateProbeView(APIView):
    """Used by tests / clients to verify non-admins are rejected."""

    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        return Response({"ok": True, "is_app_admin": True})
