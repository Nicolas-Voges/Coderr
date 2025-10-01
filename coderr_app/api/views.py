from rest_framework import viewsets, status, generics, mixins
from coderr_app.models import Offer, Detail
from rest_framework.permissions import IsAuthenticated
from .serializers import OfferSerializer, DetailSerializer
from .permissions import IsTypeBusiness, IsOwner, IsSuperUser

class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = []
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, IsTypeBusiness]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif 'update' in self.action or self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]
    

    def get_queryset(self):
        queryset = Offer.objects.all()
        page_size_param = self.request.query_params.get('page_size',12)

        creator_id_param = self.request.query_params.get('creator_id',None)
        if creator_id_param is not None:
            queryset = queryset.filter(user_id=creator_id_param)

        min_price_param = self.request.query_params.get('min_price',None)
        if min_price_param is not None:
            queryset = queryset.filter(min_price__lte=min_price_param)

        max_delivery_time_param = self.request.query_params.get('max_delivery_time',None)
        if max_delivery_time_param is not None:
            queryset = queryset.filter(max_delivery_time_param__lte=max_delivery_time_param)

        ordering_param = self.request.query_params.get('ordering',None)
        if ordering_param is not None:
            queryset = queryset.order_by(ordering_param)

        search_param = self.request.query_params.get('search',None) 
        if search_param is not None:
            queryset = queryset.filter(title__icontains=search_param)
            queryset = queryset.filter(description__icontains=search_param)
        queryset = queryset.all()[:page_size_param]
        return queryset
    

class DetailRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DetailSerializer
    queryset = Detail.objects.all()