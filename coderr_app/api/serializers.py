from django.contrib.auth.models import User
from django.utils import timezone
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

    details = serializers.SerializerMethodField(many=True, view_name='detail-detail')

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
        if len(value) != 3:
            raise serializers.ValidationError('An offer must contain 3 details!')
        
        types = {detail.offer_type.lower() for detail in value}

        required = {"basic", "standard", "premium"}
        
        if types != required:
            raise serializers.ValidationError('Only one detail may be specified for each offer type!')
        
        return value
    

    def get_details(self, obj):
        view = self.context.get('view')

        serializer_class = (
            DetailHyperLinkSerializer if view and view.action in ['list', 'retrieve']
            else DetailSerializer
        )

        return serializer_class(obj.details.all(), many=True, context=self.context)


    def create(self, validated_data):
        created_at = timezone.now()
        updated_at = None
        if validated_data['image'] not in [None, ""]:
            updated_at = timezone.now()

        offer = Offer(
            title=validated_data['title'],
            image=validated_data['image'],
            description=validated_data['description'],
            details=validated_data['details'],
            created_at=created_at,
            updated_at=updated_at
        )

        for detail in validated_data.details:
            Detail.objects.create(
                title=detail['title'],
                revisions=detail['revisions'],
                delivery_time_in_days=detail['delivery_time_in_days'],
                price=detail['price'],
                features=detail['features'],
                offer_type=detail['offer_type']
            )
        
        return offer