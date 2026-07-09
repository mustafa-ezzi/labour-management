from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db import transaction
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.api.permissions import IsAuthenticatedCompanyMember, user_company_ids
from apps.api.serializers import (
    AttendanceSerializer,
    BulkAttendanceSerializer,
    BulkLabourPaymentSerializer,
    LabourPaymentSerializer,
    LabourSerializer,
    LabourTokenObtainPairSerializer,
    RegisterSerializer,
    SiteSerializer,
)
from apps.labour_payments.services import record_labour_payment
from apps.attendance.models import Attendance
from apps.labour.balance import site_pending_as_of
from apps.labour.models import Labour
from apps.labour_payments.models import LabourPayment
from apps.sites.models import Site

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token_serializer = LabourTokenObtainPairSerializer(
            data={"email": user.email, "password": request.data.get("password", "")}
        )
        token_serializer.is_valid(raise_exception=True)
        return Response(token_serializer.validated_data, status=status.HTTP_201_CREATED)


class LabourTokenObtainPairView(TokenObtainPairView):
    serializer_class = LabourTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]

    def get(self, request):
        membership = (
            request.user.company_memberships.select_related("company")
            .order_by("created_at")
            .first()
        )
        if not membership:
            return Response({"detail": "No company membership."}, status=400)
        c = membership.company
        return Response(
            {
                "user": {
                    "id": str(request.user.id),
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                },
                "company": {
                    "id": str(c.id),
                    "name": c.name,
                    "role": membership.role,
                },
            }
        )


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        ids = user_company_ids(self.request.user)
        return Site.objects.filter(company_id__in=ids).select_related("company")

    def perform_create(self, serializer):
        membership = (
            self.request.user.company_memberships.select_related("company")
            .order_by("created_at")
            .first()
        )
        serializer.save(
            company=membership.company,
            created_by=self.request.user,
        )


class LabourViewSet(viewsets.ModelViewSet):
    serializer_class = LabourSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        ids = user_company_ids(self.request.user)
        qs = (
            Labour.objects.filter(company_id__in=ids)
            .select_related("site", "company")
            .prefetch_related("attendances", "payments")
        )
        site_id = self.request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(site_id=site_id)
        st = self.request.query_params.get("status")
        if st:
            qs = qs.filter(status=st)
        return qs


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        ids = user_company_ids(self.request.user)
        qs = Attendance.objects.filter(company_id__in=ids).select_related("labour", "site")
        site_id = self.request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(site_id=site_id)
        labour_id = self.request.query_params.get("labour_id")
        if labour_id:
            qs = qs.filter(labour_id=labour_id)
        d = self.request.query_params.get("date")
        if d:
            qs = qs.filter(date=d)
        return qs

    @action(detail=False, methods=["get"], url_path="day-summary")
    def day_summary(self, request):
        site_id = request.query_params.get("site_id")
        day = request.query_params.get("date")
        if not site_id or not day:
            return Response(
                {"detail": "Query parameters site_id and date are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        allowed = user_company_ids(request.user)
        site = Site.objects.filter(pk=site_id, company_id__in=allowed).first()
        if not site:
            return Response({"detail": "Site not found."}, status=status.HTTP_404_NOT_FOUND)

        earned = (
            Attendance.objects.filter(
                company_id=site.company_id,
                site_id=site_id,
                date=day,
                present=True,
            ).aggregate(total=Sum("wage_rate"))["total"]
            or Decimal("0")
        )

        paid = (
            LabourPayment.objects.filter(
                company_id=site.company_id,
                payment_date=day,
                labour__site_id=site_id,
            ).aggregate(total=Sum("amount_paid"))["total"]
            or Decimal("0")
        )

        # Cumulative outstanding for the site through this date (unpaid from prior days carries forward).
        pending = site_pending_as_of(site, day)
        pending_carried = pending - earned + paid
        roster_cap = (
            Labour.objects.filter(
                company_id=site.company_id,
                site_id=site_id,
                status="active",
            ).aggregate(total=Sum("daily_wage"))["total"]
            or Decimal("0")
        )

        return Response(
            {
                "site_id": str(site_id),
                "date": day,
                "total_earned_today": str(earned),
                "total_paid_today": str(paid),
                "total_pending_today": str(pending),
                "total_pending_carried_forward": str(pending_carried),
                "total_roster_daily": str(roster_cap),
            }
        )

    @action(detail=False, methods=["post"], url_path="bulk-mark")
    def bulk_mark(self, request):
        ser = BulkAttendanceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        site_id = ser.validated_data["site_id"]
        day = ser.validated_data["date"]
        marks = ser.validated_data["marks"]
        allowed_companies = user_company_ids(request.user)
        site = Site.objects.filter(pk=site_id, company_id__in=allowed_companies).first()
        if not site:
            return Response({"detail": "Site not found."}, status=status.HTTP_404_NOT_FOUND)
        labour_ids = {m["labour_id"] for m in marks}
        valid_ids = set(
            Labour.objects.filter(
                site_id=site_id,
                company_id=site.company_id,
                pk__in=labour_ids,
            ).values_list("pk", flat=True)
        )
        if valid_ids != labour_ids:
            return Response(
                {"detail": "One or more workers are not on this site."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            for m in marks:
                Attendance.objects.update_or_create(
                    labour_id=m["labour_id"],
                    date=day,
                    defaults={
                        "company_id": site.company_id,
                        "site_id": site_id,
                        "present": m["present"],
                        "overtime_hours": m.get("overtime_hours"),
                        "notes": m.get("notes") or "",
                    },
                )
        return Response({"saved": len(marks)}, status=status.HTTP_200_OK)


class LabourPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = LabourPaymentSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        ids = user_company_ids(self.request.user)
        qs = LabourPayment.objects.filter(company_id__in=ids).select_related("labour")
        labour_id = self.request.query_params.get("labour_id")
        if labour_id:
            qs = qs.filter(labour_id=labour_id)
        site_id = self.request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(labour__site_id=site_id)
        return qs

    @action(detail=False, methods=["post"], url_path="bulk-pay")
    def bulk_pay(self, request):
        ser = BulkLabourPaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        pay_date = ser.validated_data["payment_date"]
        notes = ser.validated_data.get("notes") or ""
        lines = ser.validated_data["payments"]
        allowed = user_company_ids(request.user)

        labour_ids = {line["labour_id"] for line in lines}
        labours = {
            lb.pk: lb
            for lb in Labour.objects.filter(
                company_id__in=allowed,
                pk__in=labour_ids,
            ).select_related("company")
        }
        if len(labours) != len(labour_ids):
            return Response(
                {"detail": "One or more workers were not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_ids = []
        total_paid = Decimal("0")
        errors = []

        with transaction.atomic():
            for line in lines:
                labour = labours[line["labour_id"]]
                try:
                    payment = record_labour_payment(
                        labour,
                        line["amount_paid"],
                        pay_date,
                        notes,
                    )
                    created_ids.append(payment.pk)
                    total_paid += payment.amount_paid
                except ValueError as exc:
                    errors.append({"labour_id": str(labour.pk), "error": str(exc)})

            if errors:
                transaction.set_rollback(True)
                return Response({"payments": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "created": len(created_ids),
                "total_paid": str(total_paid),
                "payment_ids": [str(pid) for pid in created_ids],
            },
            status=status.HTTP_201_CREATED,
        )


class HealthView(APIView):
    """Lightweight health check for Railway / uptime monitors."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok"})

