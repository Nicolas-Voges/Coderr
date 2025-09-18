from django.urls import path, include
from .views import OfferViewSet, DetailRetrieveView
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet, basename='offers')

urlpatterns = [
    path('offers/', include(router.urls)),
    path('offerdetails/<int:pk>/', DetailRetrieveView.as_view(), name='detail-detail'),
]