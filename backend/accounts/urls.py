# Reference: PROMPT.md → Authentication & User Roles → Key API Endpoints
# Purpose: Authentication endpoints for login, register, and user management

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'accounts'

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints (to be implemented)
    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('me/', views.UserProfileView.as_view(), name='user_profile'),
    # path('users/', views.UserListView.as_view(), name='user_list'),
]