from decimal import Decimal

from django.db.models import Avg, Count, DecimalField, Max, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.permissions import user_company_ids
from apps.companies.models import CompanyMembership

from .models import Material, MaterialUsage
from .serializers import MaterialSerializer, MaterialUsageSerializer


def _user_company(user):
    """Return the first CompanyMembership company for a user, or None."""
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

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], url_path="site-summary")
    def site_summary(self, request):
        """
        Returns per-site material expense totals.
        ?site_id=<uuid> filters to one site.
        """
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

        data = [
            {
                "id": str(m.id),
                "name": m.name,
                "unit_of_measure": m.unit_of_measure,
                "rate_per_unit": str(m.rate_per_unit),
                "total_quantity_used": str(m.total_quantity_used),
                "total_amount_spent": str(m.total_amount_spent),
                "usage_count": m.usage_count,
            }
            for m in qs
        ]
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
        # calculated_amount is set inside model.save()
        serializer.save()

    @action(detail=False, methods=["get"], url_path="day-summary")
    def day_summary(self, request):
        """
        Returns total material cost for a given site + date.
        Query params: site_id (required), usage_date (required)
        """
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

        total_cost = sum(e.calculated_amount for e in entries)
        return Response(
            {
                "site_id": site_id,
                "usage_date": usage_date,
                "total_cost": str(total_cost),
                "entry_count": entries.count(),
                "entries": MaterialUsageSerializer(entries, many=True).data,
            }
        )
