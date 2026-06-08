from rest_framework import serializers

from apps.sites.models import Site

from decimal import Decimal

from .balance import usage_paid_total, usage_pending_amount
from .models import Material, MaterialPayment, MaterialUsage
from .services import record_material_payment


class MaterialSerializer(serializers.ModelSerializer):
    site_id = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.all(),
        source="site",
    )

    total_quantity_used = serializers.DecimalField(
        max_digits=14, decimal_places=3, read_only=True, default="0.000"
    )
    total_amount_spent = serializers.DecimalField(
        max_digits=16, decimal_places=2, read_only=True, default="0.00"
    )
    total_amount_paid = serializers.DecimalField(
        max_digits=16, decimal_places=2, read_only=True, default="0.00"
    )
    pending_amount = serializers.SerializerMethodField()
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
            "total_amount_paid",
            "pending_amount",
            "latest_usage_date",
            "usage_count",
            "average_daily_usage",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_pending_amount(self, obj: Material) -> str:
        spent = getattr(obj, "total_amount_spent", None)
        paid = getattr(obj, "total_amount_paid", None)
        if spent is not None and paid is not None:
            return str(Decimal(str(spent)) - Decimal(str(paid)))
        from .balance import material_pending_amount

        return str(material_pending_amount(obj))


class MaterialUsageSerializer(serializers.ModelSerializer):
    material_id = serializers.PrimaryKeyRelatedField(
        queryset=Material.objects.all(),
        source="material",
    )
    material_name = serializers.CharField(source="material.name", read_only=True)
    unit_of_measure = serializers.CharField(source="material.unit_of_measure", read_only=True)
    rate_per_unit = serializers.DecimalField(
        source="material.rate_per_unit", max_digits=12, decimal_places=2, read_only=True
    )
    amount_paid = serializers.SerializerMethodField()
    pending_amount = serializers.SerializerMethodField()

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
            "amount_paid",
            "pending_amount",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "calculated_amount", "created_at"]

    def get_amount_paid(self, obj: MaterialUsage) -> str:
        return str(usage_paid_total(obj))

    def get_pending_amount(self, obj: MaterialUsage) -> str:
        return str(usage_pending_amount(obj))


class MaterialPaymentSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(read_only=True)
    site_id = serializers.UUIDField(read_only=True)
    material_id = serializers.PrimaryKeyRelatedField(
        queryset=Material.objects.all(),
        source="material",
    )
    material_usage_id = serializers.PrimaryKeyRelatedField(
        queryset=MaterialUsage.objects.all(),
        source="material_usage",
        required=False,
        allow_null=True,
    )
    material_name = serializers.CharField(source="material.name", read_only=True)

    class Meta:
        model = MaterialPayment
        fields = [
            "id",
            "company_id",
            "site_id",
            "material_id",
            "material_usage_id",
            "material_name",
            "payment_type",
            "amount_paid",
            "payment_date",
            "remaining_amount",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "company_id",
            "site_id",
            "payment_type",
            "remaining_amount",
            "material_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        material = attrs.get("material")
        usage = attrs.get("material_usage")
        if usage and usage.material_id != material.pk:
            raise serializers.ValidationError(
                {"material_usage_id": "Usage entry does not belong to this material."}
            )
        amount = attrs.get("amount_paid")
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({"amount_paid": "Amount must be greater than zero."})
        return attrs

    def create(self, validated_data):
        material = validated_data.pop("material")
        usage = validated_data.pop("material_usage", None)
        pay_date = validated_data.pop("payment_date")
        amount = validated_data.pop("amount_paid")
        notes = validated_data.pop("notes", "") or ""
        try:
            return record_material_payment(material, amount, pay_date, notes, usage)
        except ValueError as exc:
            raise serializers.ValidationError({"amount_paid": str(exc)}) from exc


class BulkMaterialPaymentLineSerializer(serializers.Serializer):
    material_id = serializers.UUIDField()
    amount_paid = serializers.DecimalField(max_digits=16, decimal_places=2)
    material_usage_id = serializers.UUIDField(required=False, allow_null=True)


class BulkMaterialPaymentSerializer(serializers.Serializer):
    payment_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True, max_length=512, default="")
    payments = BulkMaterialPaymentLineSerializer(many=True)

    def validate_payments(self, value):
        if not value:
            raise serializers.ValidationError("Select at least one material to pay.")
        return value
