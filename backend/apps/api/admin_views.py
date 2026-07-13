"""App Admin API — Phase 1–2: access control + account management."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.account_admin import (
    AccountDeleteError,
    hard_delete_account,
    serialize_account,
)
from apps.accounts.audit import AdminAuditLog
from apps.accounts.audit_services import write_admin_audit
from apps.api.admin_dashboard import AdminDashboardView, AdminSensitiveThrottle
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
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        return Response({"ok": True, "is_app_admin": True})


def _get_customer_user(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError):
        return None
    if user.is_superuser:
        return None
    return user


class AdminAccountListView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        qs = User.objects.filter(is_superuser=False).order_by("-date_joined")
        q = (request.query_params.get("q") or "").strip()
        status_filter = (request.query_params.get("status") or "").strip().lower()

        if q:
            qs = qs.filter(
                Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(owned_companies__name__icontains=q)
                | Q(company_memberships__company__name__icontains=q)
            ).distinct()

        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "disabled":
            qs = qs.filter(is_active=False)

        results = [serialize_account(u) for u in qs[:200]]
        return Response({"count": len(results), "results": results})


class AdminAccountDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get_throttles(self):
        if getattr(self, "request", None) is not None and self.request.method == "DELETE":
            return [AdminSensitiveThrottle()]
        return []

    def get(self, request, user_id):
        user = _get_customer_user(user_id)
        if not user:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_account(user))

    def patch(self, request, user_id):
        user = _get_customer_user(user_id)
        if not user:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        changed = []

        if "email" in data:
            email = str(data["email"]).strip().lower()
            if not email:
                return Response({"email": ["Email is required."]}, status=400)
            if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
                return Response({"email": ["A user with this email already exists."]}, status=400)
            user.email = email
            changed.append("email")

        if "first_name" in data:
            user.first_name = str(data["first_name"] or "")[:150]
            changed.append("first_name")

        if "last_name" in data:
            user.last_name = str(data["last_name"] or "")[:150]
            changed.append("last_name")

        if "is_active" in data:
            user.is_active = bool(data["is_active"])
            changed.append("is_active")

        user.save()

        company_name = data.get("company_name")
        if company_name is not None:
            company = user.owned_companies.order_by("created_at").first()
            if not company:
                membership = (
                    user.company_memberships.select_related("company")
                    .order_by("created_at")
                    .first()
                )
                company = membership.company if membership else None
            if company:
                company.name = str(company_name).strip()[:255] or company.name
                company.save(update_fields=["name"])
                changed.append("company_name")

        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.UPDATE_USER,
            summary=f"Updated account {user.email}",
            target_type="user",
            target_id=str(user.pk),
            metadata={"fields": changed},
        )
        return Response(serialize_account(user))

    def delete(self, request, user_id):
        user = _get_customer_user(user_id)
        if not user:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        confirm = str((request.data or {}).get("confirm") or "").strip()
        company = user.owned_companies.order_by("created_at").first()
        expected = company.name if company else "DELETE"
        if confirm != expected and confirm != "DELETE":
            return Response(
                {
                    "detail": "Confirmation does not match.",
                    "hint": f'Type the workspace name "{expected}" or DELETE to confirm.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = user.email
        try:
            summary = hard_delete_account(target_user=user, actor=request.user)
        except AccountDeleteError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.DELETE_USER,
            summary=f"Deleted account {email}",
            target_type="user",
            target_id=str(user_id),
            metadata=summary,
        )
        return Response({"deleted": True, **summary}, status=status.HTTP_200_OK)


class AdminAccountDisableView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def post(self, request, user_id):
        user = _get_customer_user(user_id)
        if not user:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        user.is_active = False
        user.save(update_fields=["is_active"])
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.DISABLE_USER,
            summary=f"Disabled account {user.email}",
            target_type="user",
            target_id=str(user.pk),
        )
        return Response(serialize_account(user))


class AdminAccountEnableView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def post(self, request, user_id):
        user = _get_customer_user(user_id)
        if not user:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        user.is_active = True
        user.save(update_fields=["is_active"])
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.ENABLE_USER,
            summary=f"Enabled account {user.email}",
            target_type="user",
            target_id=str(user.pk),
        )
        return Response(serialize_account(user))
