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

from apps.api.permissions import IsAuthenticatedCompanyMember, is_app_admin, user_company_ids
from apps.api.serializers import (
    AttendanceSerializer,
    BulkAttendanceSerializer,
    BulkDailyWageSerializer,
    BulkLabourPaymentSerializer,
    LabourPaymentSerializer,
    LabourSerializer,
    LabourTokenObtainPairSerializer,
    RegisterSerializer,
    SiteSerializer,
)
from apps.labour_payments.services import record_labour_payment
from apps.attendance.models import Attendance
from apps.labour.balance import labour_pending_wage, site_pending_as_of
from apps.labour.models import Labour
from apps.labour.services import record_daily_wage_entry
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
    """Current user profile. App Admin may have no company membership."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_active:
            return Response(
                {"detail": "This account has been disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        admin = is_app_admin(request.user)
        payload = {
            "user": {
                "id": str(request.user.id),
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "is_app_admin": admin,
                "is_active": request.user.is_active,
            },
            "company": None,
        }

        membership = (
            request.user.company_memberships.select_related("company")
            .order_by("created_at")
            .first()
        )
        if membership:
            c = membership.company
            payload["company"] = {
                "id": str(c.id),
                "name": c.name,
                "role": membership.role,
            }
        elif not admin:
            return Response({"detail": "No company membership."}, status=400)

        return Response(payload)


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

    @action(detail=False, methods=["get"], url_path="daily-wages")
    def daily_wages(self, request):
        """Combined roster for the Daily Wages screen: one row per active
        worker with today's wage/paid/pending plus the running balance."""
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

        labours = Labour.objects.filter(
            site_id=site_id, company_id=site.company_id, status="active"
        ).order_by("name")
        attendances = {
            a.labour_id: a
            for a in Attendance.objects.filter(site_id=site_id, date=day)
        }
        payments = {
            p.attendance_id: p
            for p in LabourPayment.objects.filter(
                labour__site_id=site_id, attendance_id__in=[a.pk for a in attendances.values()]
            )
        }

        results = []
        for lb in labours:
            att = attendances.get(lb.pk)
            payment = payments.get(att.pk) if att else None
            wage_today = att.wage_rate if (att and att.present) else Decimal("0")
            paid_today = payment.amount_paid if payment else Decimal("0")
            results.append(
                {
                    "labour_id": str(lb.pk),
                    "name": lb.name,
                    "daily_wage": str(lb.daily_wage),
                    "wage_today": str(wage_today),
                    "paid_today": str(paid_today),
                    "pending_today": str(wage_today - paid_today),
                    "pending_wage": str(labour_pending_wage(lb, day)),
                }
            )

        return Response({"site_id": str(site_id), "date": day, "results": results})

    @action(detail=False, methods=["post"], url_path="bulk-wage-entry")
    def bulk_wage_entry(self, request):
        """Save a full day of "wage of the day" + "amount paid" entries at
        once — the combined attendance+pay flow (Daily Wages)."""
        ser = BulkDailyWageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        site_id = ser.validated_data["site_id"]
        day = ser.validated_data["date"]
        notes = ser.validated_data.get("notes") or ""
        entries = ser.validated_data["entries"]
        allowed_companies = user_company_ids(request.user)
        site = Site.objects.filter(pk=site_id, company_id__in=allowed_companies).first()
        if not site:
            return Response({"detail": "Site not found."}, status=status.HTTP_404_NOT_FOUND)

        labour_ids = {e["labour_id"] for e in entries}
        labours = {
            lb.pk: lb
            for lb in Labour.objects.filter(
                site_id=site_id, company_id=site.company_id, pk__in=labour_ids
            )
        }
        if len(labours) != len(labour_ids):
            return Response(
                {"detail": "One or more workers are not on this site."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        errors = []
        with transaction.atomic():
            for entry in entries:
                labour = labours[entry["labour_id"]]
                try:
                    attendance, payment, pending_wage = record_daily_wage_entry(
                        labour,
                        day,
                        entry.get("wage_amount") or Decimal("0"),
                        entry.get("amount_paid") or Decimal("0"),
                        notes,
                    )
                    results.append(
                        {
                            "labour_id": str(labour.pk),
                            "wage_today": str(attendance.wage_rate if attendance.present else Decimal("0")),
                            "paid_today": str(payment.amount_paid) if payment else "0",
                            "pending_wage": str(pending_wage),
                        }
                    )
                except ValueError as exc:
                    errors.append({"labour_id": str(labour.pk), "error": str(exc)})

            if errors:
                transaction.set_rollback(True)
                return Response({"entries": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"saved": len(results), "results": results}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="worker-history")
    def worker_history(self, request):
        """Present-day calendar for one worker in a given month."""
        import calendar
        from datetime import date

        site_id = request.query_params.get("site_id")
        labour_id = request.query_params.get("labour_id")
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        if not site_id or not labour_id or not year or not month:
            return Response(
                {"detail": "Query parameters site_id, labour_id, year, and month are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            year_i = int(year)
            month_i = int(month)
            if month_i < 1 or month_i > 12:
                raise ValueError
        except ValueError:
            return Response({"detail": "Invalid year or month."}, status=status.HTTP_400_BAD_REQUEST)

        allowed = user_company_ids(request.user)
        site = Site.objects.filter(pk=site_id, company_id__in=allowed).first()
        if not site:
            return Response({"detail": "Site not found."}, status=status.HTTP_404_NOT_FOUND)

        labour = Labour.objects.filter(
            pk=labour_id, site_id=site_id, company_id=site.company_id
        ).first()
        if not labour:
            return Response({"detail": "Worker not found on this site."}, status=status.HTTP_404_NOT_FOUND)

        last_day = calendar.monthrange(year_i, month_i)[1]
        start = date(year_i, month_i, 1)
        end = date(year_i, month_i, last_day)

        attendances = Attendance.objects.filter(
            company_id=site.company_id,
            site_id=site_id,
            labour_id=labour_id,
            date__gte=start,
            date__lte=end,
            present=True,
        ).order_by("date")

        days = [
            {"date": str(att.date), "wage_rate": str(att.wage_rate)}
            for att in attendances
        ]

        return Response(
            {
                "site_id": str(site_id),
                "labour_id": str(labour_id),
                "labour_name": labour.name,
                "year": year_i,
                "month": month_i,
                "present_count": len(days),
                "days": days,
            }
        )


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

