from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as account_views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', account_views.admin_portal_login, name='admin_portal'),
    path('', include('artworks.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
