from django.http import Http404
from django.views.static import serve
import os
from django.conf import settings

def serve_docs(request, path):
    # Default to index.html if the path is empty (e.g., /docs/)
    if not path:
        path = 'index.html'
    
    # Try to serve the file from the built mkdocs 'site' directory
    try:
        return serve(request, path, document_root=settings.DOCS_ROOT)
    except Http404:
        # Handle cases where mkdocs uses directory/index.html structure
        if not path.endswith('index.html'):
            return serve(request, os.path.join(path, 'index.html'), document_root=settings.DOCS_ROOT)
        raise Http404("Docs not found")

    