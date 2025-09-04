from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from collections import OrderedDict
from auth_app.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = [
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "location",
                "tel",
                "description",
                "working_hours",
                "type",
                "email",
                "created_at",
                "uploaded_at"
            }
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        path = request.path
        type = rep.get('type')
        if type == 'customer':
            ordered = {
                "user": rep.get('user.id'),
                "username": rep.get('user.username'),
                "first_name": rep.get('user.first_name'),
                "last_name": rep.get('user.last_name'),
                "file": rep.get('file'),
                "uploaded_at": rep.get('uploaded_at'),
                "type": type
            }
            return ordered
        else:
            ordered = {
                "user": rep.get('user.id'),
                "username": rep.get('user.username'),
                "first_name": rep.get('user.first_name'),
                "last_name": rep.get('user.last_name'),
                "file": rep.get('file'),
                "location": rep.get('location'),
                "tel": rep.get('tel'),
                "description": rep.get('description'),
                "working_hours": rep.get('working_hours'),
                "type": type
            }
            return ordered


class RegistrationSerializer(serializers.ModelSerializer):


    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=Profile._meta.get_field('type').choices)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'repeated_password',
            'type',
            'id'
        ]
        extra_kwargs = {'password': {'write_only': True}, 'repeated_password': {'write_only': True}}

    
    def validate(self, validated_data):
        if validated_data['password'] != validated_data['repeated_password']:
            raise serializers.ValidationError({'Password': "Password do not match!"})
        return validated_data
    

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(password)
        user.save()

        Profile.objects.create(
            user=user,
            type=user_type,
            created_at=timezone.now()
        )

        return user