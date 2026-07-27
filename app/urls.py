# Main URL patterns
from app.discover import autodiscover_exposed_apis
from django.urls import path

from app.docs import serve_docs


urlpatterns = [
    # path('admin/', admin.site.urls),
    *autodiscover_exposed_apis(),

    path('docs/', serve_docs, {'path': ''}),
    path('docs/<path:path>', serve_docs),
]