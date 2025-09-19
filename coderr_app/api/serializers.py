from django.contrib.auth.models import User
from rest_framework import serializers
from coderr_app.models import Offer, Detail

class DetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Detail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type'
        ]


class DetailHyperLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Detail
        fields = [
            'id',
            'url'
        ]


class OfferSerializer(serializers.ModelSerializer):

    details = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='detail-detail')

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'ceated_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]

    
    def validate_details(self, value):
        if value.count() != 3:
            raise serializers.ValidationError('An offer must contain 3 details!')
        type_1 = False
        type_2 = False
        type_3 = False
        
        for detail in value:
            if detail.offer_type.lower() == 'basic':
                type_1 = True
            if detail.offer_type.lower() == 'standard':
                type_2 = True
            if detail.offer_type.lower() == 'premium':
                type_3 = True
        
        if not type_1 and type_2 and type_3:
            raise serializers.ValidationError('Only one detail may be specified for each offer type!')
        
        return value