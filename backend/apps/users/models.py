"""
User models for BookGen-AI.
Custom User model with extended profile and analytics.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
import secrets
import hashlib


class UserManager(BaseUserManager):
    """Custom manager for User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier.
    Includes email verification and password reset functionality.
    """
    
    # Basic fields
    email = models.EmailField(
        unique=True,
        db_index=True,
        error_messages={'unique': 'A user with that email already exists.'}
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Password reset
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['date_joined']),
            models.Index(fields=['email_verification_token']),
            models.Index(fields=['password_reset_token']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        """Return the user's short name (first name)."""
        return self.first_name or self.email.split('@')[0]
    
    def generate_email_verification_token(self):
        """Generate a secure token for email verification."""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = timezone.now()
        self.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
        return self.email_verification_token
    
    def generate_password_reset_token(self):
        """Generate a secure token for password reset."""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_sent_at = timezone.now()
        self.save(update_fields=['password_reset_token', 'password_reset_sent_at'])
        return self.password_reset_token
    
    def verify_email(self):
        """Mark email as verified and clear the token."""
        self.email_verified = True
        self.email_verification_token = None
        self.email_verification_sent_at = None
        self.save(update_fields=['email_verified', 'email_verification_token', 'email_verification_sent_at'])


class SubscriptionPlan(models.Model):
    """
    Subscription tiers for the SaaS platform.
    Defines limits and features for different levels.
    """
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('forever', 'Forever'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    duration_days = models.IntegerField(default=30)
    book_limit_per_month = models.IntegerField(default=5)
    features = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'subscription plan'
        verbose_name_plural = 'subscription plans'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Extended user profile with subscription, analytics, and preferences.
    One-to-one relationship with User model.
    """
    
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    
    # Relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Subscription management
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profiles'
    )
    subscription_status = models.CharField(
        max_length=20,
        default='active'
    )
    current_month_book_count = models.IntegerField(default=0)
    usage_reset_date = models.DateTimeField(default=timezone.now)
    
    # Avatar (placeholder system - random icon)
    avatar_seed = models.CharField(max_length=50, blank=True)  # Seed for identicon generation
    
    # Comprehensive analytics
    total_books_generated = models.IntegerField(default=0)
    total_words_written = models.IntegerField(default=0)
    total_edit_actions = models.IntegerField(default=0)
    total_time_spent_minutes = models.IntegerField(default=0)
    last_active_at = models.DateTimeField(auto_now=True)
    
    # Feature usage tracking (JSON field)
    features_used = models.JSONField(default=dict, blank=True)
    # Example: {"book_generation": 5, "book_editing": 23, "cover_generation": 3}
    
    # Preferences
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def get_avatar_initials(self):
        """Get user initials for placeholder avatar."""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        return self.user.email[:2].upper()
    
    def increment_feature_usage(self, feature_name):
        """Increment usage count for a specific feature."""
        if not self.features_used:
            self.features_used = {}
        self.features_used[feature_name] = self.features_used.get(feature_name, 0) + 1
        self.save(update_fields=['features_used'])
    
    def update_analytics(self, books=0, words=0, edits=0, minutes=0):
        """Update analytics counters."""
        self.total_books_generated += books
        self.total_words_written += words
        self.total_edit_actions += edits
        self.total_time_spent_minutes += minutes
        self.save(update_fields=[
            'total_books_generated',
            'total_words_written',
            'total_edit_actions',
            'total_time_spent_minutes'
        ])


class UserAnalytics(models.Model):
    """
    Detailed analytics tracking for user actions.
    Real-time event tracking with metadata.
    Stored in SQLite for fast querying.
    """
    
    EVENT_TYPES = [
        ('book_generated', 'Book Generated'),
        ('book_edited', 'Book Edited'),
        ('cover_created', 'Cover Created'),
        ('pdf_downloaded', 'PDF Downloaded'),
        ('api_call', 'API Call'),
        ('session_start', 'Session Start'),
        ('session_end', 'Session End'),
    ]
    
    # Relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    
    # Event details
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    metadata = models.JSONField(default=dict, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'user_analytics'
        verbose_name = 'user analytics'
        verbose_name_plural = 'user analytics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.event_type} at {self.created_at}"
    
    @classmethod
    def track_event(cls, user, event_type, metadata=None, duration=None):
        """
        Track a user event with optional metadata and duration.
        
        Args:
            user: User instance
            event_type: Type of event (must be in EVENT_TYPES)
            metadata: Optional dict with event-specific data
            duration: Optional duration in seconds
        """
        return cls.objects.create(
            user=user,
            event_type=event_type,
            metadata=metadata or {},
            duration_seconds=duration
        )


# Note: Books, Domains, Niches data will be stored in MongoDB via PyMongo
# See apps/core/mongodb.py for MongoDB operations


# Signal to create UserProfile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created."""
    if created:
        # Generate avatar seed (for identicon)
        avatar_seed = hashlib.md5(instance.email.encode()).hexdigest()[:12]
        UserProfile.objects.create(user=instance, avatar_seed=avatar_seed)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
