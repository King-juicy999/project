"""
Custom User and Profile models for the Django REST API.

This module defines:
- Custom User model extending AbstractBaseUser and PermissionsMixin
- Profile model with user-specific information
- UserManager for handling user creation
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom User Manager for handling user creation.
    
    Provides methods for creating regular users and superusers
    with proper validation and default values.
    """
    
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular user.
        
        Args:
            email (str): User's email address (required)
            username (str): User's username (required)
            password (str): User's password (optional)
            **extra_fields: Additional fields for the user
            
        Returns:
            User: The created user instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError('Email is required')
        
        # Normalize email to lowercase
        email = self.normalize_email(email)
        
        # Create user instance
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a superuser.
        
        Args:
            email (str): Superuser's email address
            username (str): Superuser's username
            password (str): Superuser's password
            **extra_fields: Additional fields for the superuser
            
        Returns:
            User: The created superuser instance
            
        Raises:
            ValueError: If required superuser fields are not set
        """
        # Set default values for superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        # Validate superuser requirements
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model extending Django's AbstractBaseUser.
    
    Uses email as the primary identifier instead of username.
    Includes additional fields for user verification and status.
    """
    
    # Core user fields
    email = models.EmailField(unique=True, help_text="User's email address (used as login)")
    username = models.CharField(max_length=150, unique=True, help_text="User's unique username")
    
    # Status fields
    is_active = models.BooleanField(default=True, help_text="Whether the user account is active")
    is_staff = models.BooleanField(default=False, help_text="Whether the user can access admin site")
    is_verified = models.BooleanField(default=False, help_text="Whether the user's email is verified")
    
    # Timestamp fields
    date_joined = models.DateTimeField(default=timezone.now, help_text="When the user joined")

    # Manager and authentication settings
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        """String representation of the user."""
        return self.email

    def get_full_name(self):
        """Get the user's full name (email in this case)."""
        return self.email

    def get_short_name(self):
        """Get the user's short name (username)."""
        return self.username


class Profile(models.Model):
    """
    User Profile model containing additional user information.
    
    Each user has exactly one profile with contact information,
    role, and personal details.
    """
    
    # Role choices for users
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    ]

    # Profile fields
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        help_text="Associated user account"
    )
    phone_number = models.CharField(
        max_length=15, 
        unique=True,
        help_text="User's phone number (must be unique)"
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='student',
        help_text="User's role in the system"
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="User's date of birth (optional)"
    )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        """String representation of the profile."""
        return f"{self.user.username}'s profile"

    def get_role_display_name(self):
        """Get the human-readable role name."""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
