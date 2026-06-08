from decimal import Decimal

from django.db import transaction
from django.db.models import Avg, Count, DecimalField, Max, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.permissions import IsAuthenticatedCompanyMember, user_company_ids
from apps.companies.models import CompanyMembership

from .models import Material, MaterialPayment, MaterialUsage
from .serializers import (
    BulkMaterialPaymentSerializer,
    MaterialPaymentSerializer,
    MaterialSerializer,
    MaterialUsageSerializer,
)
from .services import record_material_payment


def _user_company(user):
    m = CompanyMembership.objects.filter(user=user).select_related("company").first()
    return m.company if m else None


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialSerializer

    def get_queryset(self):
        company = _user_company(self.request.user)
        if not company:
            return Material.objects.none()

        qs = (
            Material.objects.filter(company=company)
            .annotate(
                total_quantity_used=Coalesce(
                    Sum("usage_entries__quantity_used"),
                    Value(Decimal("0.000")),
                    output_field=DecimalField(max_digits=14, decimal_places=3),
                ),
                total_amount_spent=Coalesce(
                    Sum("usage_entries__calculated_amount"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=16, decimal_places=2),
                ),
                total_amount_paid=Coalesce(
                    Sum("payments__amount_paid"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=16, decimal_places=2),
                ),
                latest_usage_date=Max("usage_entries__usage_date"),
                usage_count=Count("usage_entries"),
                average_daily_usage=Coalesce(
                    Avg("usage_entries__quantity_used"),
                    Value(Decimal("0.000")),
                    output_field=DecimalField(max_digits=14, decimal_places=3),
                ),
            )
            .select_related("site")
        )

        site_id = self.request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(site_id=site_id)

        return qs

    def perform_create(self, serializer):
        company = _user_company(self.request.user)
        serializer.save(company=company)

    @action(detail=False, methods=["get"], url_path="site-summary")
    def site_summary(self, request):
        company = _user_company(request.user)
        if not company:
            return Response({"results": []})

        qs = (
            Material.objects.filter(company=company)
            .annotate(
                total_amount_spent=Coalesce(
                    Sum("usage_entries__calculated_amount"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=16, decimal_places=2),
                ),
                total_amount_paid=Coalesce(
                    Sum("payments__amount_paid"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=16, decimal_places=2),
                ),
                total_quantity_used=Coalesce(
                    Sum("usage_entries__quantity_used"),
                    Value(Decimal("0.000")),
                    output_field=DecimalField(max_digits=14, decimal_places=3),
                ),
                usage_count=Count("usage_entries"),
            )
        )

        site_id = request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(site_id=site_id)

        data = []
        for m in qs:
            spent = Decimal(str(m.total_amount_spent))
            paid = Decimal(str(m.total_amount_paid))
            data.append(
                {
                    "id": str(m.id),
                    "name": m.name,
                    "unit_of_measure": m.unit_of_measure,
                    "rate_per_unit": str(m.rate_per_unit),
                    "total_quantity_used": str(m.total_quantity_used),
                    "total_amount_spent": str(spent),
                    "total_amount_paid": str(paid),
                    "pending_amount": str(spent - paid),
                    "usage_count": m.usage_count,
                }
            )
        return Response({"results": data})


class MaterialUsageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialUsageSerializer

    def get_queryset(self):
        company_ids = user_company_ids(self.request.user)
        qs = MaterialUsage.objects.filter(
            material__company_id__in=company_ids
        ).select_related("material")

        material_id = self.request.query_params.get("material_id")
        if material_id:
            qs = qs.filter(material_id=material_id)

        site_id = self.request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(site_id=site_id)

        usage_date = self.request.query_params.get("usage_date")
        if usage_date:
            qs = qs.filter(usage_date=usage_date)

        return qs

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], url_path="day-summary")
    def day_summary(self, request):
        site_id = request.query_params.get("site_id")
        usage_date = request.query_params.get("usage_date")

        if not site_id or not usage_date:
            return Response(
                {"detail": "site_id and usage_date are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company_ids = user_company_ids(request.user)
        entries = MaterialUsage.objects.filter(
            site_id=site_id,
            usage_date=usage_date,
            material__company_id__in=company_ids,
        ).select_related("material")

        total_cost = Decimal("0")
        total_paid = Decimal("0")
        total_pending = Decimal("0")
        serialized = MaterialUsageSerializer(entries, many=True).data
        for row in serialized:
            total_cost += Decimal(str(row["calculated_amount"]))
            total_paid += Decimal(str(row["amount_paid"]))
            total_pending += Decimal(str(row["pending_amount"]))

        return Response(
            {
                "site_id": site_id,
                "usage_date": usage_date,
                "total_cost": str(total_cost),
                "total_paid": str(total_paid),
                "total_pending": str(total_pending),
                "entry_count": entries.count(),
                "entries": serialized,
            }
        )


class MaterialPaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]
    serializer_class = MaterialPaymentSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        company_ids = user_company_ids(self.request.user)
        qs = MaterialPayment.objects.filter(company_id__in=company_ids).select_related(
            "material", "material_usage"
        )

        material_id = self.request.query_params.get("material_id")
        if material_id:
            qs = qs.filter(material_id=material_id)

        site_id = self.request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(site_id=site_id)

        material_usage_id = self.request.query_params.get("material_usage_id")
        if material_usage_id:
            qs = qs.filter(material_usage_id=material_usage_id)

        return qs

    @action(detail=False, methods=["post"], url_path="bulk-pay")
    def bulk_pay(self, request):
        ser = BulkMaterialPaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        pay_date = ser.validated_data["payment_date"]
        notes = ser.validated_data.get("notes") or ""
        lines = ser.validated_data["payments"]
        allowed = user_company_ids(request.user)

        material_ids = {line["material_id"] for line in lines}
        materials = {
            m.pk: m
            for m in Material.objects.filter(
                company_id__in=allowed,
                pk__in=material_ids,
            ).select_related("company", "site")
        }
        if len(materials) != len(material_ids):
            return Response(
                {"detail": "One or more materials were not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usage_ids = {line["material_usage_id"] for line in lines if line.get("material_usage_id")}
        usages = {}
        if usage_ids:
            usages = {
                u.pk: u
                for u in MaterialUsage.objects.filter(
                    material__company_id__in=allowed,
                    pk__in=usage_ids,
                ).select_related("material")
            }
            if len(usages) != len(usage_ids):
                return Response(
                    {"detail": "One or more usage entries were not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        created_ids = []
        total_paid = Decimal("0")
        errors = []

        with transaction.atomic():
            for line in lines:
                material = materials[line["material_id"]]
                usage = None
                usage_id = line.get("material_usage_id")
                if usage_id:
                    usage = usages[usage_id]
                try:
                    payment = record_material_payment(
                        material,
                        line["amount_paid"],
                        pay_date,
                        notes,
                        usage,
                    )
                    created_ids.append(payment.pk)
                    total_paid += payment.amount_paid
                except ValueError as exc:
                    key = str(usage_id) if usage_id else str(material.pk)
                    errors.append({"id": key, "error": str(exc)})

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
