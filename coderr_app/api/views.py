from django.db.models import Q
from rest_framework import viewsets, status, generics, mixins
from coderr_app.models import Offer, Detail, Order
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed
from .serializers import OfferSerializer, DetailSerializer, OrderSerializer
from .permissions import IsTypeBusiness, IsTypeCustomer, IsOwner, IsSuperUser, IsStaffUser
from .paginations import ResultsSetPagination

class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    pagination_class = ResultsSetPagination

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

        creator_id_param = self.request.query_params.get('creator_id',None)
        if creator_id_param is not None:
            queryset = queryset.filter(user_id=creator_id_param)

        min_price_param = self.request.query_params.get('min_price',None)
        if min_price_param is not None:
            queryset = queryset.filter(details__price__lte=min_price_param)

        max_delivery_time_param = self.request.query_params.get('max_delivery_time',None)
        if max_delivery_time_param is not None:
            queryset = queryset.filter(details__delivery_time_in_days__lte=max_delivery_time_param)

        ordering_param = self.request.query_params.get('ordering',None)
        if ordering_param is not None:
            if ordering_param == 'created_at':
                queryset = queryset.order_by(ordering_param)
            elif ordering_param == 'min_price':
                queryset = queryset.order_by('details__price')


        search_param = self.request.query_params.get('search',None) 
        if search_param is not None:
            queryset = queryset.filter(
                Q(title__icontains=search_param) | Q(description__icontains=search_param)
            )

        return queryset
    

class DetailRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DetailSerializer
    queryset = Detail.objects.all()


class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        user = self.request.user
        profile_type = user.profile.type  

        if profile_type == "customer":
            return Order.objects.filter(customer_user=user)

        elif profile_type == "business":
            return Order.objects.filter(business_user=user)
        
        return Order.objects.none()

    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated, ]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, IsTypeCustomer]
        elif 'update' in self.action:
            permission_classes = [IsAuthenticated, IsTypeBusiness, IsOwner]
        elif self.action == 'destroy':
            permission_classes = [IsSuperUser, IsStaffUser]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]
    
    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')