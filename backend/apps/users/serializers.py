"""
Serializers for User authentication and profile management.
Includes comprehensive validation and error handling.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate
from .models import User, UserProfile, UserAnalytics
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with validation."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        # Check email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Enter a valid email address.")
        
        # Check uniqueness
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value.lower()
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        # Additional custom validation
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        """Create new user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials."""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        # Authenticate user
        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")
        
        attrs['user'] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if user exists (but don't reveal if they don't for security)."""
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    
    token = serializers.CharField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data."""
    
    avatar_initials = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar_seed',
            'avatar_initials',
            'subscription_tier',
            'total_books_generated',
            'total_words_written',
            'total_edit_actions',
            'total_time_spent_minutes',
            'last_active_at',
            'features_used',
            'theme',
            'email_notifications',
            'marketing_emails',
        ]
        read_only_fields = [
            'avatar_seed',
            'subscription_tier',
            'total_books_generated',
            'total_words_written',
            'total_edit_actions',
            'total_time_spent_minutes',
            'last_active_at',
            'features_used',
        ]
    
    def get_avatar_initials(self, obj):
        """Get user initials for avatar."""
        return obj.get_avatar_initials()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data with profile."""
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'email_verified',
            'is_active',
            'date_joined',
            'profile',
        ]
        read_only_fields = [
            'id',
            'email',
            'email_verified',
            'is_active',
            'date_joined',
        ]
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return obj.get_full_name()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
    
    def validate_first_name(self, value):
        """Validate first name."""
        if value and len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters.")
        return value
    
    def validate_last_name(self, value):
        """Validate last name."""
        if value and len(value) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters.")
        return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile preferences."""
    
    class Meta:
        model = UserProfile
        fields = ['theme', 'email_notifications', 'marketing_emails']


class UserAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for user analytics data."""
    
    class Meta:
        model = UserAnalytics
        fields = ['event_type', 'metadata', 'duration_seconds', 'created_at']
        read_only_fields = fields


class UserAnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for aggregated analytics summary."""
    
    total_books = serializers.IntegerField()
    total_words = serializers.IntegerField()
    total_edits = serializers.IntegerField()
    total_time_minutes = serializers.IntegerField()
    recent_activity = UserAnalyticsSerializer(many=True)
    feature_usage = serializers.DictField()
