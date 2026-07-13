from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.attendance.models import Attendance
from apps.companies.models import Company, CompanyMembership, CompanyRole
from apps.labour.balance import labour_earned_total, labour_paid_total, labour_pending_wage
from apps.labour.models import Labour
from apps.labour_payments.models import LabourPayment, PaymentType
from apps.labour_payments.services import record_labour_payment
from apps.sites.models import Site

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    company_name = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        email = validated_data["email"]
        user = User.objects.create_user(
            email=email,
            password=validated_data["password"],
            first_name=validated_data.get("first_name") or "",
            last_name=validated_data.get("last_name") or "",
        )
        company = Company.objects.create(
            name=validated_data["company_name"],
            owner=user,
        )
        CompanyMembership.objects.create(
            user=user,
            company=company,
            role=CompanyRole.OWNER,
        )
        return user


class LabourTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_app_admin"] = bool(user.is_superuser and user.is_active)
        membership = (
            user.company_memberships.select_related("company").order_by("created_at").first()
        )
        if membership:
            token["company_id"] = str(membership.company_id)
            token["role"] = membership.role
        return token

    def validate(self, attrs):
        email = (attrs.get(self.username_field) or "").strip().lower()
        if email:
            attrs[self.username_field] = email
            existing = User.objects.filter(email__iexact=email).first()
            if existing and not existing.is_active:
                from rest_framework_simplejwt.exceptions import AuthenticationFailed

                raise AuthenticationFailed(
                    "This account has been disabled. Contact LabourPro support.",
                    code="user_disabled",
                )
        data = super().validate(attrs)
        data["is_app_admin"] = bool(self.user.is_superuser and self.user.is_active)
        return data


class SiteSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(read_only=True)
    to_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Site
        fields = (
            "id",
            "company_id",
            "name",
            "location",
            "from_date",
            "to_date",
            "total_work_days",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "company_id",
            "total_work_days",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")
        if self.instance:
            from_date = from_date or self.instance.from_date
            to_date = to_date if "to_date" in attrs else self.instance.to_date
        if from_date and to_date and to_date < from_date:
            raise serializers.ValidationError({"to_date": "End date cannot be before start date."})
        return attrs


class LabourSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(read_only=True)
    site_id = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.none(),
        source="site",
    )
    earned_total = serializers.SerializerMethodField()
    paid_total = serializers.SerializerMethodField()
    pending_wage = serializers.SerializerMethodField()

    class Meta:
        model = Labour
        fields = (
            "id",
            "company_id",
            "site_id",
            "name",
            "daily_wage",
            "phone_number",
            "status",
            "earned_total",
            "paid_total",
            "pending_wage",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "company_id", "created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        qs = Site.objects.none()
        if request and getattr(request.user, "is_authenticated", False):
            qs = Site.objects.filter(
                company_id__in=request.user.company_memberships.values_list(
                    "company_id", flat=True
                )
            )
        self.fields["site_id"].queryset = qs
        self.fields["site_id"].required = self.instance is None

    def get_earned_total(self, obj: Labour):
        return str(labour_earned_total(obj))

    def get_paid_total(self, obj: Labour):
        return str(labour_paid_total(obj))

    def get_pending_wage(self, obj: Labour):
        return str(labour_pending_wage(obj))

    def validate_site_id(self, value):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Missing request context.")
        allowed = set(
            request.user.company_memberships.values_list("company_id", flat=True)
        )
        if value.company_id not in allowed:
            raise serializers.ValidationError("Invalid site for your company.")
        return value

    def create(self, validated_data):
        site = validated_data.pop("site")
        validated_data.pop("company", None)
        return Labour.objects.create(
            site=site,
            company=site.company,
            **validated_data,
        )

    def update(self, instance, validated_data):
        site = validated_data.pop("site", None)
        validated_data.pop("company", None)
        if site is not None:
            validated_data["site"] = site
            validated_data["company"] = site.company
        return super().update(instance, validated_data)


class AttendanceSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(read_only=True)
    wage_rate = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Attendance
        fields = (
            "id",
            "company_id",
            "labour_id",
            "site_id",
            "date",
            "present",
            "overtime_hours",
            "wage_rate",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "company_id", "wage_rate", "created_at", "updated_at")

    def validate(self, attrs):
        labour_id = attrs.get("labour_id")
        site_id = attrs.get("site_id")
        if self.instance:
            labour_id = labour_id or self.instance.labour_id
            site_id = site_id or self.instance.site_id
        if labour_id and site_id:
            labour_obj = Labour.objects.filter(pk=labour_id).first()
            if not labour_obj or str(labour_obj.site_id) != str(site_id):
                raise serializers.ValidationError("Labour must belong to the selected site.")
        request = self.context.get("request")
        if request and site_id:
            allowed = Site.objects.filter(
                company_id__in=request.user.company_memberships.values_list(
                    "company_id", flat=True
                )
            ).filter(pk=site_id)
            if not allowed.exists():
                raise serializers.ValidationError("Invalid site for your company.")
        return attrs


class AttendanceMarkItemSerializer(serializers.Serializer):
    labour_id = serializers.UUIDField()
    present = serializers.BooleanField(default=True)
    overtime_hours = serializers.DecimalField(
        max_digits=6, decimal_places=2, required=False, allow_null=True
    )
    notes = serializers.CharField(required=False, allow_blank=True, max_length=512)


class BulkAttendanceSerializer(serializers.Serializer):
    site_id = serializers.UUIDField()
    date = serializers.DateField()
    marks = AttendanceMarkItemSerializer(many=True)


class DailyWageEntrySerializer(serializers.Serializer):
    labour_id = serializers.UUIDField()
    wage_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True, default=Decimal("0")
    )
    amount_paid = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True, default=Decimal("0")
    )

    def validate_wage_amount(self, value):
        return value if value is not None else Decimal("0")

    def validate_amount_paid(self, value):
        return value if value is not None else Decimal("0")


class BulkDailyWageSerializer(serializers.Serializer):
    site_id = serializers.UUIDField()
    date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True, max_length=512, default="")
    entries = DailyWageEntrySerializer(many=True)


class LabourPaymentSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = LabourPayment
        fields = (
            "id",
            "company_id",
            "labour_id",
            "attendance_id",
            "payment_type",
            "amount_paid",
            "payment_date",
            "remaining_amount",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "company_id",
            "payment_type",
            "remaining_amount",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        labour = attrs.get("labour")
        labour_id = attrs.get("labour_id")
        if labour is None and labour_id:
            labour = Labour.objects.filter(pk=labour_id).first()
        if labour is None:
            raise serializers.ValidationError({"labour_id": "Labour is required."})
        attendance_id = attrs.get("attendance_id")
        if attendance_id:
            att = Attendance.objects.filter(pk=attendance_id, labour_id=labour.pk).first()
            if not att:
                raise serializers.ValidationError(
                    {"attendance_id": "Attendance does not belong to this labour."}
                )
        amount = attrs.get("amount_paid")
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({"amount_paid": "Amount must be greater than zero."})
        return attrs

    def create(self, validated_data):
        labour = validated_data.pop("labour")
        pay_date = validated_data.pop("payment_date")
        amount = validated_data.pop("amount_paid")
        notes = validated_data.pop("notes", "") or ""
        try:
            return record_labour_payment(labour, amount, pay_date, notes)
        except ValueError as exc:
            raise serializers.ValidationError({"amount_paid": str(exc)}) from exc


class BulkPaymentLineSerializer(serializers.Serializer):
    labour_id = serializers.UUIDField()
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2)


class BulkLabourPaymentSerializer(serializers.Serializer):
    payment_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True, max_length=512, default="")
    payments = BulkPaymentLineSerializer(many=True)

    def validate_payments(self, value):
        if not value:
            raise serializers.ValidationError("Select at least one worker to pay.")
        return value


