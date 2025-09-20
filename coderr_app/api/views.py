from rest_framework import viewsets, status, generics, mixins
from coderr_app.models import Offer, Detail
from rest_framework.permissions import IsAuthenticated
from .serializers import OfferSerializer, DetailSerializer
from .permissions import IsTypeBusiness, IsOwner

class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsTypeBusiness]
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        if self.action == 'update' or self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in permission_classes]

class DetailRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DetailSerializer
    queryset = Detail.objects.all()