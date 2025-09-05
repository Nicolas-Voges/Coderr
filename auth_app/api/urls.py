from django.urls import path
from .views import RegistrationView, LoginView, ProfileUpdateRetriveView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name="registration"),
    path('login/', LoginView.as_view(), name="login"),
    path('profile/<int:pk>/', ProfileUpdateRetriveView.as_view(), name="profile-detail"),
]