from django.urls import path, include
from .views import OfferViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet, basename='offers')

urlpatterns = [
    path('offers/', include(router.urls)),
    path('offerdetails/<int:pk>/', name='detail-detail' ),
]