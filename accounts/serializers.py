"""
Serializers for the Django REST API.

This module contains:
- ProfileSerializer: For handling user profile data
- UserSerializer: For handling user registration with nested profile
- LoginSerializer: For handling user authentication
"""

from rest_framework import serializers
from .models import User, Profile
import re


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User Profile model.
    
    Handles validation for phone number format and role selection.
    """
    
    class Meta:
        model = Profile
        fields = ['phone_number', 'role', 'date_of_birth']

    def validate_phone_number(self, value):
        """
        Validate phone number format and uniqueness.
        
        Args:
            value (str): Phone number to validate
            
        Returns:
            str: Validated phone number
            
        Raises:
            ValidationError: If phone number is invalid or already exists
        """
        if not value:
            raise serializers.ValidationError("Phone number is required")
        
        # Remove any whitespace for validation
        cleaned_number = value.strip()
        
        # Basic pattern for phone numbers (allows digits, spaces, dashes, parentheses, plus)
        pattern = r'^[\d\s\-\(\)\+]+$'
        if not re.match(pattern, cleaned_number):
            raise serializers.ValidationError("Invalid phone number format. Use only digits, spaces, dashes, parentheses, and plus signs.")
        
        # Check minimum length (at least 10 digits)
        digits_only = re.sub(r'[^\d]', '', cleaned_number)
        if len(digits_only) < 10:
            raise serializers.ValidationError("Phone number must contain at least 10 digits.")
        
        # Check if phone number already exists (excluding current instance if updating)
        qs = Profile.objects.filter(phone_number=cleaned_number)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This phone number is already registered.")
        
        return cleaned_number

    def validate_role(self, value):
        """
        Validate user role selection.
        
        Args:
            value (str): Role to validate
            
        Returns:
            str: Validated role
            
        Raises:
            ValidationError: If role is invalid
        """
        valid_roles = ['student', 'vendor', 'admin']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return value


class UserReadSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for returning user details with nested profile.

    Purpose: Keep serializers focused on serialization/deserialization only.
    Creation and business logic happen in views.
    """

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active', 'date_joined', 'is_verified', 'profile']
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """
    Input serializer for registration payload validation only.

    Logic moved to view: object creation, authentication, tokens, and responses.
    """

    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    profile = ProfileSerializer()

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_username(self, value):
        username = value.strip()
        if len(username) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username is already taken.")
        return username

    def validate(self, data):
        # Keep only minimal, payload-level validation here.
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        # Normalize email and drop password_confirm from the cleaned output
        data = dict(data)
        data['email'] = data['email'].lower().strip()
        data.pop('password_confirm', None)
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login payload validation only.

    Business logic (authentication, permissions, and token generation)
    is handled in the views to maintain separation of concerns.
    """

    email = serializers.EmailField(help_text="User's email address")
    password = serializers.CharField(help_text="User's password")

    def validate(self, data):
        """
        Validate basic presence and normalize inputs. Authentication happens in views.
        """
        email = (data.get('email') or '').lower().strip()
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        return {"email": email, "password": password}