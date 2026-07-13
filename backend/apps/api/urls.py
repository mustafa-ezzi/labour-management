from django.urls import include, path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView

from apps.api.admin_views import (
    AdminAccountDetailView,
    AdminAccountDisableView,
    AdminAccountEnableView,
    AdminAccountListView,
    AdminAuditListView,
    AdminDashboardView,
    AdminGateProbeView,
    AdminMeView,
)
from apps.api.views import (
    AttendanceViewSet,
    HealthView,
    LabourPaymentViewSet,
    LabourTokenObtainPairView,
    LabourViewSet,
    MeView,
    RegisterView,
    SiteViewSet,
)
from apps.materials.views import (
    MaterialPaymentViewSet,
    MaterialUsageViewSet,
    MaterialViewSet,
)

router = DefaultRouter()
router.register("sites", SiteViewSet, basename="site")
router.register("labours", LabourViewSet, basename="labour")
router.register("attendance", AttendanceViewSet, basename="attendance")
router.register("labour-payments", LabourPaymentViewSet, basename="labour-payment")
router.register("materials", MaterialViewSet, basename="material")
router.register("material-usage", MaterialUsageViewSet, basename="material-usage")
router.register("material-payments", MaterialPaymentViewSet, basename="material-payment")

admin_urlpatterns = [
    path("me/", AdminMeView.as_view(), name="admin-me"),
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("audit/", AdminAuditListView.as_view(), name="admin-audit"),
    path("gate/", AdminGateProbeView.as_view(), name="admin-gate"),
    path("accounts/", AdminAccountListView.as_view(), name="admin-accounts"),
    path("accounts/<uuid:user_id>/", AdminAccountDetailView.as_view(), name="admin-account-detail"),
    path(
        "accounts/<uuid:user_id>/disable/",
        AdminAccountDisableView.as_view(),
        name="admin-account-disable",
    ),
    path(
        "accounts/<uuid:user_id>/enable/",
        AdminAccountEnableView.as_view(),
        name="admin-account-enable",
    ),
]

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LabourTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("admin/", include((admin_urlpatterns, "admin-api"))),
    path("", include(router.urls)),
]
