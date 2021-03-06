from django.contrib import admin
from django.urls import path, include

from pythonyanssound.swagger import urlpatterns as swagger_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/profile/', include('profiles.urls')),
    path('api/music/', include('music.urls')),
    path('api/playlist/', include('playlists.urls')),
    path('api/search/', include('search.urls')),
]

urlpatterns += swagger_urlpatterns
