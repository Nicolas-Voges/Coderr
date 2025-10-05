from django.urls import path, include
from .views import OfferViewSet, DetailRetrieveView, OrderViewSet, OrderCountView
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('offerdetails/<int:pk>/', DetailRetrieveView.as_view(), name='detail-detail'),
    path('order-count/<int:pk>/', OrderCountView.as_view(), name='orders-detail-in_progress'), 
    path('completed-order-count/<int:pk>/', OrderCountView.as_view(), name='orders-detail-completed')
]