from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ExportDownloadView, OrderViewSet

router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")

urlpatterns = [
    path(
        "exports/<int:pk>/download/",
        ExportDownloadView.as_view(),
        name="export-download",
    ),
]


urlpatterns += router.urls
