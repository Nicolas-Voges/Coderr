"""
API routing for the Coderr app using DRF routers and custom endpoints.
"""

from django.urls import path, include

from rest_framework import routers

from .views import OfferViewSet, DetailRetrieveView, OrderViewSet, OrderCountView, ReviewViewSet, BaseInfoApiView

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('offerdetails/<int:pk>/', DetailRetrieveView.as_view(), name='detail-detail'),
    path('order-count/<int:pk>/', OrderCountView.as_view(), name='orders-detail-in_progress'), 
    path('completed-order-count/<int:pk>/', OrderCountView.as_view(), name='orders-detail-completed'),
    path('base-info/', BaseInfoApiView.as_view(), name='base_info')
]