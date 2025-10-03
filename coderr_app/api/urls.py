from django.urls import path, include
from .views import OfferViewSet, DetailRetrieveView, OrderViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('offerdetails/<int:pk>/', DetailRetrieveView.as_view(), name='detail-detail'),
]