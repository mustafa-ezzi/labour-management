"""Phase 5 — Admin dashboard KPIs, search, and CSV exports."""

from __future__ import annotations

import csv
from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.accounts.audit import AdminAuditLog
from apps.api.permissions import IsAppAdmin
from apps.companies.models import Company, Subscription, SubscriptionStatus
from apps.companies.subscription_services import serialize_subscription
from apps.support.models import SupportTicket
from apps.support.services import admin_unread_count, open_ticket_count, serialize_ticket

User = get_user_model()


class AdminSensitiveThrottle(UserRateThrottle):
    """Limit destructive Admin actions (delete account)."""

    scope = "admin_sensitive"
    rate = "30/hour"


class SupportCreateThrottle(UserRateThrottle):
    """Limit User support ticket creation."""

    scope = "support_create"
    rate = "20/hour"


def _signup_series(days: int = 30) -> list[dict]:
    now = timezone.now()
    start = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = (
        User.objects.filter(is_superuser=False, date_joined__gte=start)
        .annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    by_day = {r["day"].isoformat(): r["count"] for r in rows if r["day"]}
    series = []
    for i in range(days):
        d = (start + timedelta(days=i)).date()
        key = d.isoformat()
        series.append({"date": key, "count": by_day.get(key, 0)})
    return series


def _estimated_mrr() -> str:
    """Rough MRR from active/trialing plan prices (yearly → /12)."""
    total = Decimal("0")
    qs = Subscription.objects.filter(
        status__in=[SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE]
    ).select_related("plan")
    for sub in qs:
        price = sub.plan.price or Decimal("0")
        days = sub.plan.duration_days or 30
        if days >= 300:
            total += price / Decimal("12")
        elif days > 0:
            total += price * (Decimal("30") / Decimal(days))
        else:
            total += price
    return str(total.quantize(Decimal("0.01")))


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        users = User.objects.filter(is_superuser=False)
        now = timezone.now()
        week = now + timedelta(days=7)
        fortnight = now + timedelta(days=14)
        active_subs = Subscription.objects.filter(
            status__in=[SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE]
        )

        expiring_qs = (
            active_subs.filter(ends_at__gte=now, ends_at__lte=fortnight)
            .select_related("company", "company__owner", "plan")
            .order_by("ends_at")[:20]
        )
        expiring = [serialize_subscription(s) for s in expiring_qs]

        audit_qs = AdminAuditLog.objects.select_related("actor")[:12]
        recent_audit = [
            {
                "id": str(row.id),
                "action": row.action,
                "summary": row.summary,
                "created_at": row.created_at.isoformat(),
                "actor_email": row.actor.email if row.actor else None,
            }
            for row in audit_qs
        ]

        open_tickets = (
            SupportTicket.objects.filter(status__in=["open", "pending"])
            .select_related("company", "created_by")
            .order_by("-updated_at")[:8]
        )

        return Response(
            {
                "total_users": users.count(),
                "active_users": users.filter(is_active=True).count(),
                "disabled_users": users.filter(is_active=False).count(),
                "total_companies": Company.objects.count(),
                "open_support_tickets": open_ticket_count(),
                "unread_support_tickets": admin_unread_count(),
                "active_subscriptions": active_subs.count(),
                "expired_subscriptions": Subscription.objects.filter(
                    status=SubscriptionStatus.EXPIRED
                ).count(),
                "cancelled_subscriptions": Subscription.objects.filter(
                    status=SubscriptionStatus.CANCELLED
                ).count(),
                "expiring_this_week": active_subs.filter(
                    ends_at__gte=now, ends_at__lte=week
                ).count(),
                "estimated_mrr": _estimated_mrr(),
                "mrr_currency": "PKR",
                "signups_last_30_days": _signup_series(30),
                "expiring_soon": expiring,
                "recent_audit": recent_audit,
                "recent_tickets": [serialize_ticket(t) for t in open_tickets],
                "phase": "5",
                "note": "Dashboard KPIs, search, and CSV export.",
            }
        )


class AdminSearchView(APIView):
    """Global Admin search: users, companies, support tickets."""

    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response(
                {
                    "q": q,
                    "users": [],
                    "companies": [],
                    "tickets": [],
                    "detail": "Type at least 2 characters.",
                }
            )

        users = User.objects.filter(is_superuser=False).filter(
            Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        ).order_by("-date_joined")[:15]

        companies = Company.objects.filter(
            Q(name__icontains=q) | Q(owner__email__icontains=q)
        ).select_related("owner")[:15]

        ticket_q = Q(subject__icontains=q) | Q(company__name__icontains=q) | Q(
            created_by__email__icontains=q
        )
        try:
            from uuid import UUID

            ticket_q |= Q(id=UUID(q))
        except (ValueError, TypeError, AttributeError):
            pass

        tickets = (
            SupportTicket.objects.filter(ticket_q)
            .select_related("company", "created_by")
            .order_by("-updated_at")[:15]
        )

        return Response(
            {
                "q": q,
                "users": [
                    {
                        "id": str(u.id),
                        "email": u.email,
                        "name": f"{u.first_name} {u.last_name}".strip(),
                        "is_active": u.is_active,
                        "href": f"/admin/accounts/{u.id}",
                    }
                    for u in users
                ],
                "companies": [
                    {
                        "id": str(c.id),
                        "name": c.name,
                        "owner_email": c.owner.email if c.owner_id else None,
                        "href": f"/admin/accounts/{c.owner_id}" if c.owner_id else "/admin/accounts",
                    }
                    for c in companies
                ],
                "tickets": [
                    {
                        "id": str(t.id),
                        "subject": t.subject,
                        "status": t.status,
                        "company_name": t.company.name,
                        "href": f"/admin/support/{t.id}",
                    }
                    for t in tickets
                ],
            }
        )


class AdminAccountsExportView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "user_id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "company_name",
                "subscription_plan",
                "subscription_status",
                "ends_at",
            ]
        )
        users = (
            User.objects.filter(is_superuser=False)
            .prefetch_related("owned_companies", "company_memberships__company")
            .order_by("-date_joined")
        )
        for u in users:
            company = u.owned_companies.order_by("created_at").first()
            if not company:
                m = u.company_memberships.select_related("company").order_by("created_at").first()
                company = m.company if m else None
            plan_key = ""
            sub_status = ""
            ends_at = ""
            if company:
                plan_key = company.subscription_plan
                try:
                    sub = company.subscription
                    plan_key = sub.plan.key
                    sub_status = sub.status
                    ends_at = sub.ends_at.isoformat()
                except Exception:
                    pass
            writer.writerow(
                [
                    str(u.id),
                    u.email,
                    u.first_name,
                    u.last_name,
                    "yes" if u.is_active else "no",
                    u.date_joined.isoformat() if u.date_joined else "",
                    company.name if company else "",
                    plan_key,
                    sub_status,
                    ends_at,
                ]
            )

        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="accounts.csv"'
        return response


class AdminSubscriptionsExportView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "subscription_id",
                "company",
                "owner_email",
                "plan",
                "status",
                "starts_at",
                "ends_at",
                "renewed_at",
                "plan_price",
                "currency",
            ]
        )
        for sub in Subscription.objects.select_related(
            "company", "company__owner", "plan"
        ).order_by("ends_at"):
            writer.writerow(
                [
                    str(sub.id),
                    sub.company.name,
                    sub.company.owner.email if sub.company.owner_id else "",
                    sub.plan.key,
                    sub.status,
                    sub.starts_at.isoformat(),
                    sub.ends_at.isoformat(),
                    sub.renewed_at.isoformat() if sub.renewed_at else "",
                    str(sub.plan.price),
                    sub.plan.currency,
                ]
            )
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="subscriptions.csv"'
        return response
