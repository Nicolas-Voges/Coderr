from rest_framework import viewsets, status, generics, mixins
from coderr_app.models import Offer, Detail
from rest_framework.permissions import IsAuthenticated
from .serializers import OfferSerializer, DetailSerializer

class OfferViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()

class DetailRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DetailSerializer
    queryset = Detail.objects.all()