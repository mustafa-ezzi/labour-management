from rest_framework import serializers

from apps.sites.models import Site
from .models import Material, MaterialUsage


class MaterialSerializer(serializers.ModelSerializer):
    site_id = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.all(),
        source="site",
    )

    # Annotated computed fields — populated by the viewset queryset
    total_quantity_used = serializers.DecimalField(
        max_digits=14, decimal_places=3, read_only=True, default="0.000"
    )
    total_amount_spent = serializers.DecimalField(
        max_digits=16, decimal_places=2, read_only=True, default="0.00"
    )
    latest_usage_date = serializers.DateField(read_only=True, allow_null=True, default=None)
    usage_count = serializers.IntegerField(read_only=True, default=0)
    average_daily_usage = serializers.DecimalField(
        max_digits=14, decimal_places=3, read_only=True, default="0.000"
    )

    class Meta:
        model = Material
        fields = [
            "id",
            "site_id",
            "name",
            "unit_of_measure",
            "rate_per_unit",
            "notes",
            "total_quantity_used",
            "total_amount_spent",
            "latest_usage_date",
            "usage_count",
            "average_daily_usage",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MaterialUsageSerializer(serializers.ModelSerializer):
    material_id = serializers.PrimaryKeyRelatedField(
        queryset=Material.objects.all(),
        source="material",
    )
    # Expose material details for display
    material_name = serializers.CharField(source="material.name", read_only=True)
    unit_of_measure = serializers.CharField(source="material.unit_of_measure", read_only=True)
    rate_per_unit = serializers.DecimalField(
        source="material.rate_per_unit", max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = MaterialUsage
        fields = [
            "id",
            "material_id",
            "material_name",
            "unit_of_measure",
            "rate_per_unit",
            "usage_date",
            "quantity_used",
            "calculated_amount",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "calculated_amount", "created_at"]
