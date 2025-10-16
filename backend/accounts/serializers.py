# Reference: PROMPT.md → Accounts Module → Data Serialization.
# Purpose: Serialize and validate user data for REST API (registration, login, and profile).
# Note: Use Django REST Framework serializers. Include nested role info if applicable.

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Reference: PROMPT.md → POST /api/auth/register/
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text='Password must meet Django validation requirements'
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'password', 'password_confirm', 'role', 'phone', 
            'address', 'date_of_birth'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_role(self, value):
        """Validate user role - customers can self-register, others need admin approval"""
        if value not in ['customer']:
            raise serializers.ValidationError(
                "Only customer accounts can be self-registered. "
                "Contact administrator for other role assignments."
            )
        return value
    
    def create(self, validated_data):
        """Create new user with encrypted password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Reference: PROMPT.md → POST /api/auth/login/
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Authenticate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Username and password required')

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data
    Reference: PROMPT.md → GET /api/auth/me/
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'phone', 'address', 'date_of_birth',
            'full_name', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        """Return formatted full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for user list (admin/manager view)
    Reference: PROMPT.md → Role-based access for user management
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'full_name', 'phone', 
            'is_active', 'date_joined', 'total_orders'
        ]
    
    def get_full_name(self, obj):
        """Return formatted full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_total_orders(self, obj):
        """Return total orders for customer users"""
        if obj.role == 'customer':
            return obj.orders.filter(status='paid').count()
        return 0

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin user creation (all roles)
    Reference: PROMPT.md → Admin creates users with any role
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'role', 'phone', 'address', 'date_of_birth',
            'is_active'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def create(self, validated_data):
        """Create user with any role (admin only)"""
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password change"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value