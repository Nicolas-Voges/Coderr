from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from collections import OrderedDict
from auth_app.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    created_at = serializers.DateTimeField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Profile
        fields = [
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
        ]


    def set_null_to_empty_str(self, value):
        if value == None:
            return ""
        else:
            return value
        

    def update_user(self, instance, validated_data):
        user_data = validated_data.get("user", {})
        user_instance = instance.user
        user_instance.first_name = user_data.get("first_name", user_instance.first_name)
        user_instance.last_name = user_data.get("last_name", user_instance.last_name)
        user_instance.email = user_data.get("email", user_instance.email)
        user_instance.save()
        

    def update(self, instance, validated_data):
        self.update_user(instance=instance, validated_data=validated_data)

        if not validated_data.get("file") == None:
            instance.file = validated_data.get("file", "")
            instance.uploaded_at = timezone.now()
            
        instance.location = validated_data.get("location", instance.location)
        instance.tel = validated_data.get("tel", instance.tel)
        instance.description = validated_data.get("description", instance.description)
        instance.working_hours = validated_data.get("working_hours", instance.working_hours)
        instance.save()

        return instance



    def to_representation(self, instance):
        rep = super().to_representation(instance)
        view = self.context.get("view")
        type = rep.get('type')
        request = self.context.get("request")

        if type == 'customer':
            ordered = {
                "user": rep.get('user'),
                "username": self.set_null_to_empty_str(rep.get('username')),
                "first_name": self.set_null_to_empty_str(rep.get('first_name')),
                "last_name": self.set_null_to_empty_str(rep.get('last_name')),
                "file": self.set_null_to_empty_str(rep.get('file')),
                "uploaded_at": rep.get('uploaded_at'),
                "type": type
            }
        else:
            ordered = {
                "user": rep.get('user'),
                "username": self.set_null_to_empty_str(rep.get('username')),
                "first_name": self.set_null_to_empty_str(rep.get('first_name')),
                "last_name": self.set_null_to_empty_str(rep.get('last_name')),
                "file": self.set_null_to_empty_str(rep.get('file')),
                "location": self.set_null_to_empty_str(rep.get('location')),
                "tel": self.set_null_to_empty_str(rep.get('tel')),
                "description": self.set_null_to_empty_str(rep.get('description')),
                "working_hours": self.set_null_to_empty_str(rep.get('working_hours')),
                "type": type
            }
        
        if view and view.__class__.__name__ == "ProfileUpdateRetriveView" or request.method == 'PATCH':
            ordered['email']=instance.user.email
            ordered['created_at']=self.set_null_to_empty_str(rep.get('created_at'))
            return ordered
        else:
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