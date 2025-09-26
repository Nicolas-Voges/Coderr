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

    details = DetailSerializer(many=True, write_only=True)
    details_output = DetailHyperLinkSerializer(many=True, read_only=True)
    user_details = serializers.SerializerMethodField()

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    min_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    min_delivery_time = serializers.IntegerField(read_only=True)


    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'details_output',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]

    
    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError('An offer must contain 3 details!')
        print(f"TYPES {value[1]['offer_type']}")
        types = {detail['offer_type'].lower() for detail in value}

        required = {"basic", "standard", "premium"}
        
        if types != required:
            raise serializers.ValidationError('Only one detail may be specified for each offer type!')
        
        return value
    

    def get_user_details(self, obj):
        view = self.context.get('view')
        if view and view.action == 'list':
            return {
                "first_name": obj.user.first_name,
                "last_name": obj.user.last_name,
                "username": obj.user.username
            }
        return None


    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        created_at = timezone.now()
        updated_at = None
        if validated_data['image'] not in [None, ""]:
            updated_at = timezone.now()

        offer = Offer.objects.create(
            user=user,
            title=validated_data['title'],
            image=validated_data['image'],
            description=validated_data['description'],
            created_at=created_at,
            updated_at=updated_at
        )

        for detail in validated_data['details']:
            Detail.objects.create(
                offer=offer,
                title=detail['title'],
                revisions=detail['revisions'],
                delivery_time_in_days=detail['delivery_time_in_days'],
                price=detail['price'],
                features=detail['features'],
                offer_type=detail['offer_type']
            )
        
        return offer


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')

        user = User.objects.get(id=instance.user.id)
        user_details = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        }

        details = instance.details.all()
        details_data = DetailSerializer(details, many=True).data
        details_data_url = DetailHyperLinkSerializer(details, many=True, context={"request": request}).data
        
        min_prices = [detail.price for detail in instance.details.all()]
        min_price = min_prices[0]
        for price in min_prices:
            if price < min_price:
                min_price = price
        
        min_delivery_times = [detail.delivery_time_in_days for detail in instance.details.all()]
        min_delivery_time = min_delivery_times[0]
        for time in min_delivery_times:
            if time < min_delivery_time:
                min_delivery_time = time
        
        ordered = {
            'id': rep.get('id'),
            'user': rep.get('user'),
            'title': rep.get('title'),
            'image': rep.get('image'),
            'description': rep.get('description'),
            'created_at': rep.get('created_at'),
            'updated_at': rep.get('updated_at'),
            'details': details_data,
            'min_price': min_price,
            'min_delivery_time': min_delivery_time
        }

        if request.method == 'GET':
            ordered['details'] = details_data_url
            if view and getattr(view, 'action', None) == 'list':
                ordered['user_details'] = user_details
                
        elif request.method == 'PATCH' or request.method == 'POST':
            ordered.pop('user')
            ordered.pop('created_at')
            ordered.pop('updated_at')
            ordered.pop('min_price')
            ordered.pop('min_delivery_time')

        return ordered