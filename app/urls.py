# Main URL patterns
from app.discover import autodiscover_exposed_apis
from django.urls import path

from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
)
from django.views.generic import TemplateView
from scalar.scalar import urlpatterns_scalar


urlpatterns = [
    # path('admin/', admin.site.urls),
    *autodiscover_exposed_apis(),

] + urlpatterns_scalar

