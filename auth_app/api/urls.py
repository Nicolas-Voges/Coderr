"""
URL routing for authentication and profile views.
"""

from django.urls import path

from .views import RegistrationView, LoginView, ProfileUpdateRetriveView, ProfileListView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name="registration"),
    path('login/', LoginView.as_view(), name="login"),
    path('profile/<int:pk>/', ProfileUpdateRetriveView.as_view(), name="profile-detail"),
    path('profiles/business/', ProfileListView.as_view(), name="profile_business-list"),
    path('profiles/customer/', ProfileListView.as_view(), name="profile_customer-list"),
]