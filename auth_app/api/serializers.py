from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from collections import OrderedDict
from auth_app.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Profile
        fields = '__all__'


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