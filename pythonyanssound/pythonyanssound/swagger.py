from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="PythonyanSound API",
      default_version='v1',
      description="Music Web Service API",
      contact=openapi.Contact(email="vitalii.manoilo3@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path(
        r'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        r'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
