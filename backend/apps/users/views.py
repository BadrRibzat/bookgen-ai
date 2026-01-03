"""
API Views for user authentication and profile management.
Implements JWT-based authentication with email verification.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import User, UserProfile, SubscriptionPlan
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserProfileUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    UserAnalyticsSummarySerializer,
    SubscriptionPlanSerializer,
    UsageSummarySerializer,
)
from .services import AuthService, UserService
import logging

logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    """Generate JWT tokens for user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    """
    User registration endpoint.
    POST /api/auth/register/
    """
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/h', method='POST'))
    def post(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Send verification email
            AuthService.send_verification_email(user)
            
            # Generate tokens
            tokens = get_tokens_for_user(user)
            
            # Serialize user data
            user_data = UserSerializer(user).data
            
            logger.info(f"New user registered: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': user_data,
                'tokens': tokens,
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Registration failed. Please check your input.',
                'details': serializer.errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    User login endpoint.
    POST /api/auth/login/
    """
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='5/15m', method='POST'))
    def post(self, request):
        """Authenticate user and return tokens."""
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            tokens = get_tokens_for_user(user)
            
            # Serialize user data
            user_data = UserSerializer(user).data
            
            # Track login event
            UserService.track_user_event(user, 'session_start')
            
            logger.info(f"User logged in: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Login successful.',
                'user': user_data,
                'tokens': tokens,
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': {
                'code': 'AUTHENTICATION_FAILED',
                'message': 'Invalid credentials.',
                'details': serializer.errors,
            }
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    User logout endpoint.
    POST /api/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    # Blacklist token if rest_framework_simplejwt.token_blacklist is installed
                    if hasattr(token, 'blacklist'):
                        token.blacklist()
                except Exception as e:
                    # Token blacklisting failed, but continue with logout
                    logger.warning(f"Token blacklist failed: {str(e)}")
            
            # Track logout event
            UserService.track_user_event(request.user, 'session_end')
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response({
                'success': True,
                'message': 'Logout successful.',
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'code': 'LOGOUT_ERROR',
                    'message': 'An error occurred during logout.',
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    Email verification endpoint.
    GET /api/auth/verify-email/{token}/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        """Verify email using token."""
        success, message, user = AuthService.verify_email_token(token)
        
        if success:
            return Response({
                'success': True,
                'message': message,
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VERIFICATION_FAILED',
                'message': message,
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    """
    Resend verification email endpoint.
    POST /api/auth/resend-verification/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @method_decorator(ratelimit(key='user', rate='3/h', method='POST'))
    def post(self, request):
        """Resend verification email to authenticated user."""
        user = request.user
        
        if user.email_verified:
            return Response({
                'success': False,
                'error': {
                    'code': 'ALREADY_VERIFIED',
                    'message': 'Email is already verified.',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send verification email
        if AuthService.send_verification_email(user):
            return Response({
                'success': True,
                'message': 'Verification email sent. Please check your inbox.',
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': {
                'code': 'EMAIL_SEND_FAILED',
                'message': 'Failed to send verification email. Please try again later.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(APIView):
    """
    Password reset request endpoint.
    POST /api/auth/password-reset/
    """
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/h', method='POST'))
    def post(self, request):
        """Send password reset email."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Send reset email
            AuthService.send_password_reset_email(email)
            
            # Always return success (don't reveal if email exists)
            return Response({
                'success': True,
                'message': 'If an account exists with this email, a password reset link has been sent.',
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid email address.',
                'details': serializer.errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation endpoint.
    POST /api/auth/password-reset-confirm/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Reset password using token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            success, message, user = AuthService.reset_password(token, password)
            
            if success:
                return Response({
                    'success': True,
                    'message': message,
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'error': {
                    'code': 'RESET_FAILED',
                    'message': message,
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input.',
                'details': serializer.errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    User profile endpoint.
    GET/PATCH /api/users/profile/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses={200: UserSerializer})
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request):
        """Get authenticated user's profile."""
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data,
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request):
        """Update user profile."""
        # Update user basic info
        user_serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        # Update profile preferences
        profile_serializer = UserProfileUpdateSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        
        if user_serializer.is_valid() and profile_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            
            # Clear cache
            cache_key = f'user_profile_{request.user.id}'
            cache.delete(cache_key)
            
            # Return updated data
            response_serializer = UserSerializer(request.user)
            
            return Response({
                'success': True,
                'message': 'Profile updated successfully.',
                'user': response_serializer.data,
            }, status=status.HTTP_200_OK)
        
        errors = {}
        if not user_serializer.is_valid():
            errors.update(user_serializer.errors)
        if not profile_serializer.is_valid():
            errors.update(profile_serializer.errors)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Profile update failed.',
                'details': errors,
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def delete(self, request):
        """Delete user account."""
        user = request.user
        user.is_active = False  # Soft delete
        user.save()
        
        # Track deletion event
        UserService.track_user_event(user, 'account_deleted')
        
        logger.info(f"User account deactivated: {user.email}")
        
        return Response({
            'success': True,
            'message': 'Account deleted successfully.',
        }, status=status.HTTP_200_OK)


class SubscriptionPlanListView(generics.ListAPIView):
    """
    List available subscription plans.
    GET /api/users/plans/
    """
    permission_classes = [permissions.AllowAny]
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer


class UserUsageView(APIView):
    """
    User usage limits and remaining books count.
    GET /api/users/usage/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: UsageSummarySerializer})
    def get(self, request):
        """Get user's current usage and limits."""
        user = request.user
        profile = user.profile
        plan = profile.subscription_plan
        
        limit = plan.book_limit_per_month if plan else 0
        remaining = max(0, limit - profile.current_month_book_count)
        
        # In a real app, check if usage_reset_date has passed and reset count
        
        data = {
            'plan_name': plan.name if plan else 'No Plan',
            'book_limit': limit,
            'current_usage': profile.current_month_book_count,
            'remaining_books': remaining,
            'usage_reset_date': profile.usage_reset_date,
        }
        
        return Response({
            'success': True,
            'usage': data,
        }, status=status.HTTP_200_OK)


class UserAnalyticsView(APIView):
    """
    User analytics endpoint.
    GET /api/users/analytics/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request):
        """Get user's analytics summary."""
        summary = UserService.get_user_analytics_summary(request.user)
        serializer = UserAnalyticsSummarySerializer(summary)
        
        return Response({
            'success': True,
            'analytics': serializer.data,
        }, status=status.HTTP_200_OK)


class UserBooksHistoryView(APIView):
    """
    User books history endpoint.
    GET /api/users/books-history/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's book generation history."""
        # This will be implemented when we create the Book model
        # For now, return empty list
        return Response({
            'success': True,
            'books': [],
            'pagination': {
                'page': 1,
                'per_page': 20,
                'total': 0,
                'pages': 0,
            }
        }, status=status.HTTP_200_OK)
