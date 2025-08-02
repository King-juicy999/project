"""
URL patterns for the accounts app.

Defines the routing for user authentication and profile management endpoints.
"""

from django.urls import path
from . import views

urlpatterns = [
    # User registration endpoint
    path('register/', views.register, name='register'),
    
    # User authentication endpoint
    path('login/', views.login, name='login'),
    
    # Current user profile endpoint (requires authentication)
    path('me/', views.me, name='me'),
] 