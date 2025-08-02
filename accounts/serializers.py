from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile
import re


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'role', 'date_of_birth']

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required")
        
        # Basic pattern for phone numbers
        pattern = r'^[\d\s\-\(\)\+]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid phone number format")
        
        if len(value) < 10:
            raise serializers.ValidationError("Phone number too short")
        
        return value

    def validate_role(self, value):
        valid_roles = ['student', 'vendor', 'admin']
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role. Must be one of: student, vendor, admin")
        return value


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password_confirm', 'is_active', 'date_joined', 'is_verified', 'profile']
        read_only_fields = ['id', 'date_joined', 'is_verified']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate(self, data):
        # Check if password_confirm is provided
        if 'password_confirm' not in data:
            raise serializers.ValidationError("You must confirm your password.")
        
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Remove password_confirm from validated data so it doesn't get saved
        data.pop('password_confirm')
        
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        
        # Safely remove password_confirm if it exists (shouldn't happen after validate)
        validated_data.pop('password_confirm', None)
        
        # Check if phone number is unique
        if Profile.objects.filter(phone_number=profile_data['phone_number']).exists():
            raise serializers.ValidationError("Phone number already exists")
        
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            data['user'] = user
        else:
            raise serializers.ValidationError("Must include email and password")
        
        return data 