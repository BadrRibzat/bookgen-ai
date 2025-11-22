"""
Business logic layer for user authentication and management.
Handles email verification, password reset, and user operations.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import timedelta
from .models import User, UserAnalytics
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def send_verification_email(user):
        """
        Send email verification link to user.
        
        Args:
            user: User instance
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Generate verification token
            token = user.generate_email_verification_token()
            
            # Build verification URL
            verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
            
            # Email context
            context = {
                'user': user,
                'verification_url': verification_url,
                'expiry_hours': 24,
            }
            
            # Send email
            subject = 'Verify your BookGen-AI email address'
            message = render_to_string('emails/verify_email.txt', context)
            html_message = render_to_string('emails/verify_email.html', context)
            
            sender = getattr(settings, 'BREVO_TRANSACTIONAL_SENDER', settings.DEFAULT_FROM_EMAIL)

            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=sender,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Verification email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def verify_email_token(token):
        """
        Verify email token and activate user account.
        
        Args:
            token: Verification token
        
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        try:
            user = User.objects.get(email_verification_token=token)
        except User.DoesNotExist:
            return False, "Invalid or expired verification token.", None
        
        # Check if token is expired (24 hours)
        if user.email_verification_sent_at:
            expiry_time = user.email_verification_sent_at + timedelta(hours=24)
            if timezone.now() > expiry_time:
                return False, "Verification token has expired. Please request a new one.", None
        
        # Check if already verified
        if user.email_verified:
            return False, "Email is already verified.", user
        
        # Verify email
        user.verify_email()
        
        logger.info(f"Email verified for user: {user.email}")
        return True, "Email verified successfully!", user
    
    @staticmethod
    def send_password_reset_email(email):
        """
        Send password reset link to user.
        
        Args:
            email: User's email address
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Find user by email
            try:
                user = User.objects.get(email=email.lower())
            except User.DoesNotExist:
                # Don't reveal if user exists (security)
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return True  # Return True to not reveal user existence
            
            # Generate reset token
            token = user.generate_password_reset_token()
            
            # Build reset URL
            reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
            
            # Email context
            context = {
                'user': user,
                'reset_url': reset_url,
                'expiry_hours': 1,
            }
            
            # Send email
            subject = 'Reset your BookGen-AI password'
            message = render_to_string('emails/password_reset.txt', context)
            html_message = render_to_string('emails/password_reset.html', context)
            
            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=getattr(settings, 'BREVO_TRANSACTIONAL_SENDER', settings.DEFAULT_FROM_EMAIL),
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Password reset email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def reset_password(token, new_password):
        """
        Reset user password using token.
        
        Args:
            token: Password reset token
            new_password: New password
        
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        try:
            user = User.objects.get(password_reset_token=token)
        except User.DoesNotExist:
            return False, "Invalid or expired reset token.", None
        
        # Check if token is expired (1 hour)
        if user.password_reset_sent_at:
            expiry_time = user.password_reset_sent_at + timedelta(hours=1)
            if timezone.now() > expiry_time:
                return False, "Reset token has expired. Please request a new one.", None
        
        # Reset password
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_sent_at = None
        user.save()
        
        logger.info(f"Password reset successful for user: {user.email}")
        
        # Send confirmation email
        try:
            send_mail(
                subject='Your BookGen-AI password has been changed',
                message='Your password was successfully changed. If you did not make this change, please contact support immediately.',
                from_email=getattr(settings, 'BREVO_TRANSACTIONAL_SENDER', settings.DEFAULT_FROM_EMAIL),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send password change confirmation: {str(e)}")
        
        return True, "Password reset successfully!", user


class UserService:
    """Service for user-related operations."""
    
    @staticmethod
    def get_user_analytics_summary(user):
        """
        Get aggregated analytics summary for user.
        
        Args:
            user: User instance
        
        Returns:
            dict: Analytics summary
        """
        profile = user.profile
        
        # Get recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_activity = UserAnalytics.objects.filter(
            user=user,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:50]
        
        return {
            'total_books': profile.total_books_generated,
            'total_words': profile.total_words_written,
            'total_edits': profile.total_edit_actions,
            'total_time_minutes': profile.total_time_spent_minutes,
            'recent_activity': recent_activity,
            'feature_usage': profile.features_used or {},
        }
    
    @staticmethod
    def track_user_event(user, event_type, metadata=None, duration=None):
        """
        Track user event and update profile analytics.
        
        Args:
            user: User instance
            event_type: Type of event
            metadata: Optional event metadata
            duration: Optional duration in seconds
        """
        # Create analytics record
        UserAnalytics.track_event(
            user=user,
            event_type=event_type,
            metadata=metadata,
            duration=duration
        )
        
        # Update profile analytics based on event type
        profile = user.profile
        
        if event_type == 'book_generated':
            profile.update_analytics(books=1)
            profile.increment_feature_usage('book_generation')
        elif event_type == 'book_edited':
            profile.update_analytics(edits=1)
            profile.increment_feature_usage('book_editing')
        elif event_type == 'cover_created':
            profile.increment_feature_usage('cover_generation')
        elif event_type == 'session_end' and duration:
            profile.update_analytics(minutes=duration // 60)
        
        logger.info(f"Event tracked for {user.email}: {event_type}")
