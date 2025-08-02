"""
Serializers for the Django REST API.

This module contains:
- ProfileSerializer: For handling user profile data
- UserSerializer: For handling user registration with nested profile
- LoginSerializer: For handling user authentication
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
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
        if Profile.objects.filter(phone_number=cleaned_number).exists():
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


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with nested Profile.
    
    Handles user registration with profile creation in a single request.
    Includes password confirmation validation.
    """
    
    profile = ProfileSerializer()
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=False,
        help_text="Confirm your password"
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'password_confirm',
            'is_active', 'date_joined', 'is_verified', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'is_verified']

    def validate_email(self, value):
        """
        Validate email uniqueness and format.
        
        Args:
            value (str): Email to validate
            
        Returns:
            str: Validated email
            
        Raises:
            ValidationError: If email already exists
        """
        # Normalize email to lowercase
        email = value.lower().strip()
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        
        return email

    def validate_username(self, value):
        """
        Validate username uniqueness and format.
        
        Args:
            value (str): Username to validate
            
        Returns:
            str: Validated username
            
        Raises:
            ValidationError: If username already exists or is invalid
        """
        username = value.strip()
        
        # Check for minimum length
        if len(username) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        
        # Check for valid characters (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username is already taken.")
        
        return username

    def validate(self, data):
        """
        Validate the complete user data including password confirmation.
        
        Args:
            data (dict): Complete user data
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if password_confirm is provided
        if 'password_confirm' not in data:
            raise serializers.ValidationError({
                'password_confirm': "You must confirm your password."
            })
        
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        
        # Remove password_confirm from validated data so it doesn't get saved
        data.pop('password_confirm')
        
        return data

    def create(self, validated_data):
        """
        Create a new user with associated profile.
        
        Args:
            validated_data (dict): Validated user and profile data
            
        Returns:
            User: The created user instance
            
        Raises:
            ValidationError: If profile creation fails
        """
        # Extract profile data
        profile_data = validated_data.pop('profile')
        
        # Safely remove password_confirm if it exists (shouldn't happen after validate)
        validated_data.pop('password_confirm', None)
        
        try:
            # Create user first
            user = User.objects.create_user(**validated_data)
            
            # Create associated profile
            Profile.objects.create(user=user, **profile_data)
            
            return user
            
        except Exception as e:
            # If anything goes wrong, clean up and raise error
            if user:
                user.delete()
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login authentication.
    
    Validates email and password combination and returns user instance.
    """
    
    email = serializers.EmailField(help_text="User's email address")
    password = serializers.CharField(help_text="User's password")

    def validate(self, data):
        """
        Validate login credentials and authenticate user.
        
        Args:
            data (dict): Login credentials
            
        Returns:
            dict: Data with authenticated user
            
        Raises:
            ValidationError: If authentication fails
        """
        email = data.get('email', '').lower().strip()
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")
        
        # Authenticate user
        user = authenticate(email=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("Your account has been deactivated. Please contact support.")
        
        # Add user to validated data
        data['user'] = user
        
        return data 