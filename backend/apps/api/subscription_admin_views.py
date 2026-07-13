"""Admin Plan + Subscription APIs (Phase 3). Expiry never disables login."""

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.audit import AdminAuditLog
from apps.accounts.audit_services import write_admin_audit
from apps.api.permissions import IsAppAdmin
from apps.companies.models import Plan, Subscription, SubscriptionStatus
from apps.companies.subscription_services import (
    cancel_subscription,
    change_subscription_plan,
    ensure_default_plans,
    renew_subscription,
    serialize_plan,
    serialize_subscription,
    set_subscription_dates,
)


def _parse_dt(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    parsed = parse_datetime(str(value))
    if parsed is None:
        raise ValueError("Invalid datetime")
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


class AdminPlanListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        ensure_default_plans()
        qs = Plan.objects.all().order_by("sort_order", "name")
        if request.query_params.get("active") == "1":
            qs = qs.filter(is_active=True)
        return Response({"results": [serialize_plan(p) for p in qs]})

    def post(self, request):
        data = request.data or {}
        key = str(data.get("key") or "").strip().lower().replace(" ", "-")
        name = str(data.get("name") or "").strip()
        if not key or not name:
            return Response({"detail": "key and name are required."}, status=400)
        if Plan.objects.filter(key=key).exists():
            return Response({"key": ["A plan with this key already exists."]}, status=400)
        try:
            price = Decimal(str(data.get("price", "0")))
            duration = int(data.get("duration_days") or 0)
        except (InvalidOperation, TypeError, ValueError):
            return Response({"detail": "Invalid price or duration_days."}, status=400)
        if duration < 1:
            return Response({"duration_days": ["Must be at least 1."]}, status=400)

        plan = Plan.objects.create(
            key=key,
            name=name,
            price=price,
            currency=str(data.get("currency") or "PKR")[:8],
            duration_days=duration,
            is_active=bool(data.get("is_active", True)),
            features=data.get("features") if isinstance(data.get("features"), dict) else {},
            sort_order=int(data.get("sort_order") or 0),
        )
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.OTHER,
            summary=f"Created plan {plan.key}",
            target_type="plan",
            target_id=str(plan.pk),
        )
        return Response(serialize_plan(plan), status=status.HTTP_201_CREATED)


class AdminPlanDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request, plan_id):
        try:
            plan = Plan.objects.get(pk=plan_id)
        except (Plan.DoesNotExist, ValueError):
            return Response({"detail": "Plan not found."}, status=404)
        return Response(serialize_plan(plan))

    def patch(self, request, plan_id):
        try:
            plan = Plan.objects.get(pk=plan_id)
        except (Plan.DoesNotExist, ValueError):
            return Response({"detail": "Plan not found."}, status=404)

        data = request.data or {}
        changed = []
        if "name" in data:
            plan.name = str(data["name"] or "").strip()[:128] or plan.name
            changed.append("name")
        if "price" in data:
            try:
                plan.price = Decimal(str(data["price"]))
            except (InvalidOperation, TypeError, ValueError):
                return Response({"price": ["Invalid price."]}, status=400)
            changed.append("price")
        if "currency" in data:
            plan.currency = str(data["currency"] or "PKR")[:8]
            changed.append("currency")
        if "duration_days" in data:
            try:
                days = int(data["duration_days"])
            except (TypeError, ValueError):
                return Response({"duration_days": ["Invalid."]}, status=400)
            if days < 1:
                return Response({"duration_days": ["Must be at least 1."]}, status=400)
            plan.duration_days = days
            changed.append("duration_days")
        if "is_active" in data:
            plan.is_active = bool(data["is_active"])
            changed.append("is_active")
        if "features" in data and isinstance(data["features"], dict):
            plan.features = data["features"]
            changed.append("features")
        if "sort_order" in data:
            try:
                plan.sort_order = int(data["sort_order"])
            except (TypeError, ValueError):
                return Response({"sort_order": ["Invalid."]}, status=400)
            changed.append("sort_order")

        plan.save()
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.OTHER,
            summary=f"Updated plan {plan.key}",
            target_type="plan",
            target_id=str(plan.pk),
            metadata={"fields": changed},
        )
        return Response(serialize_plan(plan))


class AdminSubscriptionListView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        ensure_default_plans()
        qs = Subscription.objects.select_related("company", "company__owner", "plan").order_by(
            "ends_at"
        )

        status_filter = (request.query_params.get("status") or "").strip().lower()
        if status_filter:
            qs = qs.filter(status=status_filter)

        q = (request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(company__name__icontains=q) | Q(company__owner__email__icontains=q)
            )

        ending_in = request.query_params.get("ending_in")
        if ending_in is not None and str(ending_in).strip() != "":
            try:
                days = int(ending_in)
            except (TypeError, ValueError):
                return Response({"ending_in": ["Must be an integer."]}, status=400)
            now = timezone.now()
            qs = qs.filter(
                status__in=[
                    SubscriptionStatus.TRIALING,
                    SubscriptionStatus.ACTIVE,
                    SubscriptionStatus.PAST_DUE,
                ],
                ends_at__gte=now,
                ends_at__lte=now + timedelta(days=days),
            )

        results = [serialize_subscription(s) for s in qs[:300]]
        return Response({"count": len(results), "results": results})


class AdminSubscriptionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request, subscription_id):
        try:
            sub = Subscription.objects.select_related(
                "company", "company__owner", "plan"
            ).get(pk=subscription_id)
        except (Subscription.DoesNotExist, ValueError):
            return Response({"detail": "Subscription not found."}, status=404)
        return Response(serialize_subscription(sub))


class AdminSubscriptionRenewView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def post(self, request, subscription_id):
        try:
            sub = Subscription.objects.select_related("company", "plan").get(pk=subscription_id)
        except (Subscription.DoesNotExist, ValueError):
            return Response({"detail": "Subscription not found."}, status=404)

        data = request.data or {}
        plan = None
        if data.get("plan_id"):
            try:
                plan = Plan.objects.get(pk=data["plan_id"])
            except (Plan.DoesNotExist, ValueError):
                return Response({"plan_id": ["Plan not found."]}, status=400)
        elif data.get("plan_key"):
            try:
                plan = Plan.objects.get(key=str(data["plan_key"]).strip().lower())
            except Plan.DoesNotExist:
                return Response({"plan_key": ["Plan not found."]}, status=400)

        days = data.get("days")
        if days is not None:
            try:
                days = int(days)
            except (TypeError, ValueError):
                return Response({"days": ["Invalid."]}, status=400)

        sub = renew_subscription(
            sub,
            plan=plan,
            days=days,
            notes=data.get("notes") if "notes" in data else None,
        )
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.RENEW_SUBSCRIPTION,
            summary=f"Renewed subscription for {sub.company.name}",
            target_type="subscription",
            target_id=str(sub.pk),
            metadata={"ends_at": sub.ends_at.isoformat(), "plan": sub.plan.key},
        )
        return Response(serialize_subscription(sub))


class AdminSubscriptionCancelView(APIView):
    """Mark subscription cancelled. Does NOT disable the user account."""

    permission_classes = [IsAuthenticated, IsAppAdmin]

    def post(self, request, subscription_id):
        try:
            sub = Subscription.objects.select_related("company", "plan").get(pk=subscription_id)
        except (Subscription.DoesNotExist, ValueError):
            return Response({"detail": "Subscription not found."}, status=404)

        notes = (request.data or {}).get("notes")
        sub = cancel_subscription(sub, notes=notes if notes is not None else None)
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.DISABLE_SUBSCRIPTION,
            summary=f"Cancelled subscription for {sub.company.name} (login unchanged)",
            target_type="subscription",
            target_id=str(sub.pk),
        )
        return Response(serialize_subscription(sub))


class AdminSubscriptionSetDatesView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def post(self, request, subscription_id):
        try:
            sub = Subscription.objects.select_related("company", "plan").get(pk=subscription_id)
        except (Subscription.DoesNotExist, ValueError):
            return Response({"detail": "Subscription not found."}, status=404)

        data = request.data or {}
        try:
            starts_at = _parse_dt(data["starts_at"]) if "starts_at" in data else None
            ends_at = _parse_dt(data["ends_at"]) if "ends_at" in data else None
        except ValueError:
            return Response({"detail": "Invalid starts_at or ends_at."}, status=400)

        status_val = data.get("status")
        if status_val and status_val not in SubscriptionStatus.values:
            return Response({"status": ["Invalid status."]}, status=400)

        sub = set_subscription_dates(
            sub,
            starts_at=starts_at,
            ends_at=ends_at,
            status=status_val,
            notes=data.get("notes") if "notes" in data else None,
        )
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.UPDATE_SUBSCRIPTION,
            summary=f"Updated subscription dates for {sub.company.name}",
            target_type="subscription",
            target_id=str(sub.pk),
            metadata={
                "starts_at": sub.starts_at.isoformat(),
                "ends_at": sub.ends_at.isoformat(),
                "status": sub.status,
            },
        )
        return Response(serialize_subscription(sub))


class AdminSubscriptionChangePlanView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def post(self, request, subscription_id):
        try:
            sub = Subscription.objects.select_related("company", "plan").get(pk=subscription_id)
        except (Subscription.DoesNotExist, ValueError):
            return Response({"detail": "Subscription not found."}, status=404)

        data = request.data or {}
        plan = None
        if data.get("plan_id"):
            try:
                plan = Plan.objects.get(pk=data["plan_id"])
            except (Plan.DoesNotExist, ValueError):
                return Response({"plan_id": ["Plan not found."]}, status=400)
        elif data.get("plan_key"):
            try:
                plan = Plan.objects.get(key=str(data["plan_key"]).strip().lower())
            except Plan.DoesNotExist:
                return Response({"plan_key": ["Plan not found."]}, status=400)
        else:
            return Response({"detail": "plan_id or plan_key required."}, status=400)

        sub = change_subscription_plan(sub, plan)
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.UPDATE_SUBSCRIPTION,
            summary=f"Changed plan to {plan.key} for {sub.company.name}",
            target_type="subscription",
            target_id=str(sub.pk),
        )
        return Response(serialize_subscription(sub))
