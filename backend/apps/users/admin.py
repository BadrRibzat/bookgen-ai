"""
Django Admin configuration for Users app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, UserAnalytics, SubscriptionPlan


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    
    list_display = [
        'email', 
        'full_name_display', 
        'email_verified_badge',
        'is_active', 
        'is_staff',
        'date_joined'
    ]
    list_filter = [
        'is_active', 
        'is_staff', 
        'is_superuser',
        'email_verified',
        'date_joined'
    ]
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Email Verification', {
            'fields': ('email_verified', 'email_verification_token', 'email_verification_sent_at'),
            'classes': ('collapse',),
        }),
        ('Password Reset', {
            'fields': ('password_reset_token', 'password_reset_sent_at'),
            'classes': ('collapse',),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def full_name_display(self, obj):
        """Display full name"""
        return obj.get_full_name()
    full_name_display.short_description = 'Full Name'
    
    def email_verified_badge(self, obj):
        """Display email verification status with badge"""
        if obj.email_verified:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">✓ Verified</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">⚠ Unverified</span>'
        )
    email_verified_badge.short_description = 'Email Status'


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Subscription Plan admin"""
    list_display = ['name', 'slug', 'price', 'book_limit_per_month', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile admin"""
    
    list_display = [
        'user_email',
        'subscription_plan_display',
        'total_books_generated',
        'total_words_written',
        'last_active_at'
    ]
    list_filter = ['subscription_plan', 'theme', 'email_notifications']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = [
        'avatar_seed',
        'total_books_generated',
        'total_words_written',
        'total_edit_actions',
        'total_time_spent_minutes',
        'features_used',
        'last_active_at',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Avatar', {'fields': ('avatar_seed',)}),
        ('Subscription', {'fields': ('subscription_plan', 'subscription_status')}),
        ('Analytics', {
            'fields': (
                'total_books_generated',
                'total_words_written',
                'total_edit_actions',
                'total_time_spent_minutes',
                'features_used',
                'last_active_at'
            ),
            'classes': ('collapse',),
        }),
        ('Preferences', {
            'fields': ('theme', 'email_notifications', 'marketing_emails'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def subscription_plan_display(self, obj):
        """Display subscription plan"""
        if obj.subscription_plan:
            return obj.subscription_plan.name
        return "No Plan"
    subscription_plan_display.short_description = 'Plan'
    subscription_plan_display.admin_order_field = 'subscription_plan__name'


@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    """User Analytics admin"""
    
    list_display = [
        'user_email',
        'event_type_badge',
        'duration_display',
        'created_at'
    ]
    list_filter = ['event_type', 'created_at']
    search_fields = ['user__email', 'event_type']
    readonly_fields = ['user', 'event_type', 'metadata', 'duration_seconds', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event', {
            'fields': ('user', 'event_type', 'duration_seconds', 'metadata'),
        }),
        ('Timestamp', {
            'fields': ('created_at',),
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def event_type_badge(self, obj):
        """Display event type with color coding"""
        colors = {
            'book_generated': '#28a745',
            'book_edited': '#17a2b8',
            'cover_created': '#ffc107',
            'pdf_downloaded': '#6f42c1',
            'api_call': '#6c757d',
            'session_start': '#007bff',
            'session_end': '#dc3545',
        }
        color = colors.get(obj.event_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 10px;">{}</span>',
            color,
            obj.get_event_type_display()
        )
    event_type_badge.short_description = 'Event'
    event_type_badge.admin_order_field = 'event_type'
    
    def duration_display(self, obj):
        """Display duration in readable format"""
        if obj.duration_seconds is None:
            return '-'
        
        seconds = obj.duration_seconds
        if seconds < 60:
            return f'{seconds}s'
        elif seconds < 3600:
            minutes = seconds // 60
            return f'{minutes}m'
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f'{hours}h {minutes}m'
    duration_display.short_description = 'Duration'
    
    def has_add_permission(self, request):
        """Disable manual creation of analytics"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Analytics are read-only"""
        return False
