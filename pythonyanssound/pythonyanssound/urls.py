from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/profile/', include('profiles.urls')),
    path('api/music/', include('music.urls')),
    path('api/playlist/', include('playlists.urls')),
    path('api/search/', include('search.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
