from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

core_urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/get-token/", obtain_auth_token),
]

prodcuts_urlpatterns = [
    path("api/products/", include("apps.products.urls")),
]


urlpatterns = [
    *core_urlpatterns,
    *prodcuts_urlpatterns,
]
