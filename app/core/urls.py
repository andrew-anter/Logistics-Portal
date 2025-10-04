from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import HealthCheckView

core_urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/get-token/", obtain_auth_token),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]

prodcuts_urlpatterns = [
    path("api/products/", include("apps.products.urls")),
]

orders_urlpatterns = [
    path("api/orders/", include("apps.orders.urls")),
]


urlpatterns = [
    *core_urlpatterns,
    *prodcuts_urlpatterns,
    *orders_urlpatterns,
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
