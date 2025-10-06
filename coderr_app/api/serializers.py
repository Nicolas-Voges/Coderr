"""
Serializers for Offer, Detail, Order, Review, and Base Info.

Handles data validation, nested serialization, and custom
representations for API responses.
"""

import os

from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import serializers

from coderr_app.models import Offer, Detail, Order, Review

class DetailSerializer(serializers.ModelSerializer):
    """Serializer for Offer detail objects."""
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
    """Serializer providing only a URL to the Detail object."""
    class Meta:
        model = Detail
        fields = [
            'id',
            'url'
        ]


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offers with nested details and custom output."""
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
        """Ensure exactly 3 details are provided when creating an offer."""
        view = self.context.get('view')
        if view.action == 'create':
            if len(value) != 3:
                raise serializers.ValidationError('An offer must contain 3 details!')

        return value
    

    def get_user_details(self, obj):
        """Return basic info about the user when listing offers."""
        view = self.context.get('view')
        if view and view.action == 'list':
            return {
                "first_name": obj.user.first_name,
                "last_name": obj.user.last_name,
                "username": obj.user.username
            }
        return None


    def create(self, validated_data):
        """Create offer and nested details."""
        request = self.context.get("request")
        user = request.user
        created_at = timezone.now()
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
    

    def update(self, instance, validated_data):
        """Update offer fields and nested details; remove old image if replaced."""
        details = validated_data.get('details')
        if details:
            for detail in details:
                if not detail.get('offer_type'):
                    raise serializers.ValidationError('Offer type is important!')
                serializer = DetailSerializer(data=detail)
                serializer.is_valid(raise_exception=True)
                detail_instance = Detail.objects.get(offer_id=instance.id, offer_type=detail['offer_type'])
                detail_instance.title = detail['title']
                detail_instance.revisions = detail['revisions']
                detail_instance.delivery_time_in_days = detail['delivery_time_in_days']
                detail_instance.price = detail['price']
                detail_instance.features = detail['features']
                detail_instance.save()

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        if validated_data.get('image'):
            old_image = instance.image
            instance.image = validated_data.get('image')
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)

        instance.updated_at = timezone.now()
        instance.save()
        return instance


    def to_representation(self, instance):
        """Custom output depending on request method and view action."""
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
    

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order objects with offer detail fields."""
    title = serializers.SerializerMethodField()
    revisions = serializers.SerializerMethodField()
    delivery_time_in_days = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    offer_type = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    customer_user = serializers.SerializerMethodField()
    business_user = serializers.SerializerMethodField()
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=Detail.objects.all(),
        source="offer_detail",
        write_only=True
    )


    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
            'offer_detail_id'
        ]


    def get_title(self, obj):
        return obj.offer_detail.title
    

    def get_revisions(self, obj):
        return obj.offer_detail.revisions
    

    def get_delivery_time_in_days(self, obj):
        return obj.offer_detail.delivery_time_in_days
    

    def get_price(self, obj):
        return obj.offer_detail.price
    

    def get_features(self, obj):
        return obj.offer_detail.features
    
    
    def get_customer_user(self, obj):
        return obj.customer_user.id


    def get_business_user(self, obj):
        offer = Offer.objects.get(id=obj.offer_detail.offer_id)
        return offer.user.id


    def get_offer_type(self, obj):
        return obj.offer_detail.offer_type


    def create(self, validated_data):
        """Create order from offer detail."""
        request = self.context.get("request")
        user = request.user
        created_at = timezone.now()
        updated_at = timezone.now()
        detail = validated_data['offer_detail']
        offer = Offer.objects.get(id=detail.offer_id)

        order = Order.objects.create(
            customer_user=user,
            business_user=offer.user,
            status='in_progress',
            offer_detail=detail,
            created_at=created_at,
            updated_at=updated_at
        )
        return order
    

class OrderCountSerializer(serializers.ModelSerializer):
    """Serializer to return order counts per business user."""
    order_count = serializers.SerializerMethodField(read_only=True)
    completed_order_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Order
        fields = [
            'order_count',
            'completed_order_count'
        ]

    def get_order_count(self, value):
        pk = self.context.get('pk')
        return Order.objects.filter(business_user_id=pk, status='in_progress').count()
    

    def get_completed_order_count(self, value):
        pk = self.context.get('pk')
        return Order.objects.filter(business_user_id=pk, status='completed').count()
    

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""
    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'reviewer',
            'created_at',
            'updated_at'
        ]

    def create(self, validated_data):
        """Create a new review if one does not already exist for the reviewer/business user."""
        request = self.context.get("request")
        reviewer = request.user
        if Review.objects.filter(business_user=validated_data['business_user'], reviewer=reviewer).exists():
            raise serializers.ValidationError('You have already reviewed this business user!')
        created_at = timezone.now()
        updated_at = timezone.now()

        review = Review.objects.create(
            reviewer=reviewer,
            business_user=validated_data['business_user'],
            created_at=created_at,
            updated_at=updated_at,
            description=validated_data['description'],
            rating=validated_data['rating']
        )

        return review
    

    def update(self, instance, validated_data):
        
        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get('description', instance.description)
        instance.updated_at = timezone.now()

        return instance
    

class BaseInfoSerializer(serializers.Serializer):
    """Serializer for aggregated base information."""
    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()