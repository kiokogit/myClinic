import inspect
import logging
import importlib
from django.urls import path, include
from django.apps import apps
from rest_framework import routers, viewsets, views
from pathlib import Path

from app.settings import LOCAL_APPS

# BASE_DIR should already be defined at the top of settings.py
BASE_DIR = Path(__file__).resolve().parent

# Configuration
API_VERSION_PREFIX = 'api/'


logger = logging.getLogger(__name__)


def discover_urls_from_module(module):
    """
    Inspects the exposed_apis module for classes with 'class_path'.
    """
    router = routers.DefaultRouter(trailing_slash=False)
    extra_patterns = []

    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ != module.__name__:
            continue

        url_path = getattr(obj, 'class_path', None)
        if not url_path:
            continue

        if issubclass(obj, viewsets.ViewSetMixin):
            router.register(url_path, viewset=obj, basename=url_path)
        elif issubclass(obj, views.APIView):
            extra_patterns.append(path(url_path, obj.as_view(), name=url_path))

    return router.urls + extra_patterns


def autodiscover_exposed_apis():
    """
    Scans all local apps and mounts their APIs using the app's LABEL 
    (from apps.py) as the base URL prefix.
    """
    all_patterns = []

    local_apps = [app for app in apps.get_app_configs() if app.name in LOCAL_APPS]
    for app_config in local_apps:
        # Only process our local apps
        
        # Look for exposed_apis.py inside the app
        module_path = f"{app_config.name}.api"   # This uses the Python path (app.name)
        
        try:
            exposed_module = importlib.import_module(module_path)

            app_urls = discover_urls_from_module(exposed_module)
            
            if app_urls:
                # === KEY CHANGE: Use app label for URL prefix ===
                # This allows you to control the URL via `label` in apps.py
                url_prefix = app_config.label.replace('_', '-')
                full_prefix = f"{API_VERSION_PREFIX}{url_prefix}/"
                
                # Include the app's URLs with namespace = label
                all_patterns.append(
                    path(
                        full_prefix, 
                        include((app_urls, module_path), namespace=app_config.name)
                    )
                )

        except ModuleNotFoundError:
            # No api.py → silently skip (normal for many apps)
            continue
        except Exception as e:
            # logger.error(f"Failed to auto-discover APIs for app '{app_config.name}': {e}")
            continue
            
    return all_patterns