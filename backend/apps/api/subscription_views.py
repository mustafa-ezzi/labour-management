"""User-facing subscription APIs — read-only alerts; never blocks app access."""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import IsAuthenticatedCompanyMember
from apps.companies.models import Plan, Subscription
from apps.companies.subscription_services import (
    company_for_user,
    ensure_default_plans,
    serialize_plan,
    serialize_subscription,
    start_trial_for_company,
)


class SubscriptionMeView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]

    def get(self, request):
        company = company_for_user(request.user)
        if not company:
            return Response({"detail": "No company membership."}, status=400)

        try:
            sub = Subscription.objects.select_related(
                "plan", "company", "company__owner"
            ).get(company=company)
        except Subscription.DoesNotExist:
            sub = start_trial_for_company(company)
            sub = Subscription.objects.select_related(
                "plan", "company", "company__owner"
            ).get(pk=sub.pk)

        payload = serialize_subscription(sub)
        if payload and payload.get("is_expired"):
            payload["message"] = (
                "Your plan has ended. Contact LabourPro to renew — your account stays "
                "active until an Admin disables it."
            )
        elif payload and payload.get("ending_soon"):
            payload["message"] = (
                f"Your plan ends in {payload['days_remaining']} day(s). "
                "Contact LabourPro to renew."
            )
        else:
            payload["message"] = None
        return Response(payload)


class SubscriptionPlansView(APIView):
    """Catalog for renew messaging."""

    permission_classes = [AllowAny]

    def get(self, request):
        ensure_default_plans()
        qs = Plan.objects.filter(is_active=True).order_by("sort_order", "name")
        return Response({"results": [serialize_plan(p) for p in qs]})
