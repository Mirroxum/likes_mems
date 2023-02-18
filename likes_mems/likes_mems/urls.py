from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from .settings import MEDIA_ROOT, MEDIA_URL, DEBUG

urlpatterns = [
    path('admin/', admin.site.urls),
]

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
