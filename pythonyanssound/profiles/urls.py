from django.urls import path
from .views import ProfileDetailView

urlpatterns = [
    path('profile/<int:user_id>/', ProfileDetailView.as_view()),
]
