from django.urls import include, path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView

from apps.api.views import (
    AttendanceViewSet,
    LabourPaymentViewSet,
    LabourTokenObtainPairView,
    LabourViewSet,
    MeView,
    RegisterView,
    SiteViewSet,
)
from apps.materials.views import MaterialViewSet, MaterialUsageViewSet

router = DefaultRouter()
router.register("sites", SiteViewSet, basename="site")
router.register("labours", LabourViewSet, basename="labour")
router.register("attendance", AttendanceViewSet, basename="attendance")
router.register("labour-payments", LabourPaymentViewSet, basename="labour-payment")
router.register("materials", MaterialViewSet, basename="material")
router.register("material-usage", MaterialUsageViewSet, basename="material-usage")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LabourTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
