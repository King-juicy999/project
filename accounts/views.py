"""
API Views for user authentication and profile management.

This module contains:
- register: User registration endpoint
- login: User authentication endpoint  
- me: Current user profile endpoint
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserReadSerializer
from .models import User, Profile


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user with profile.
    
    Accepts user and profile data in a single request and creates
    both the user account and associated profile. Returns JWT tokens
    for immediate authentication.
    
    Args:
        request: HTTP request containing user and profile data
        
    Returns:
        Response: JSON with user data and JWT tokens
        
    Example Request:
        {
            "email": "user@example.com",
            "username": "username",
            "password": "password123",
            "password_confirm": "password123",
            "profile": {
                "phone_number": "1234567890",
                "role": "student",
                "date_of_birth": "1990-01-01"
            }
        }
    """
    # Validate user + profile input only; creation happens below
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Use database transaction to ensure data consistency
            with transaction.atomic():
                # Create User and Profile inside the view to keep serializers lean.
                validated = serializer.validated_data
                profile_data = validated.pop('profile')
                user = User.objects.create_user(**validated)
                Profile.objects.create(user=user, **profile_data)
                
                # Moved token generation into the view to keep serializers focused
                # on creation/validation only.
                refresh = RefreshToken.for_user(user)

                return Response({
                    'message': 'User registered successfully',
                    'user': UserReadSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    },
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': 'Registration failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate user and return JWT tokens.
    
    Validates email and password combination and returns
    user data along with JWT access and refresh tokens.
    
    Args:
        request: HTTP request containing login credentials
        
    Returns:
        Response: JSON with user data and JWT tokens
        
    Example Request:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        # Authentication moved out of the serializer and into the view.
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Django's authenticate expects "username" which maps to USERNAME_FIELD (email)
        user = authenticate(username=email, password=password)

        if not user:
            return Response({
                'error': 'Authentication failed',
                'details': {'non_field_errors': ['Invalid email or password.']}
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({
                'error': 'Authentication failed',
                'details': {'non_field_errors': ['Your account has been deactivated. Please contact support.']}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT tokens in the view
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'user': UserReadSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Authentication failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Get current authenticated user's profile.
    
    Returns the complete user data including profile information
    for the currently authenticated user.
    
    Args:
        request: HTTP request (must include valid JWT token)
        
    Returns:
        Response: JSON with current user data
        
    Authentication:
        Requires valid JWT access token in Authorization header
    """
    try:
        serializer = UserReadSerializer(request.user)
        return Response({
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve user data',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
