from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid


class Domain(models.Model):
    """Pre-defined domains/niches available for book generation"""
    name = models.CharField(max_length=100, unique=True)  # e.g., 'cybersecurity', 'ai_ml'
    display_name = models.CharField(max_length=200)  # e.g., 'Cybersecurity', 'AI & Machine Learning'
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon identifier
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    trending_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-trending_score', 'name']

    def __str__(self):
        return self.display_name


class BookGenerationRequest(models.Model):
    """Track book generation requests and limits"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

    # MongoDB reference
    mongodb_book_id = models.CharField(max_length=24, blank=True)  # MongoDB ObjectId as string

    title = models.CharField(max_length=500)
    custom_prompt = models.TextField(blank=True)
    target_word_count = models.PositiveIntegerField(default=50000)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Processing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # LLM response tracking
    llm_request_id = models.CharField(max_length=100, blank=True)
    tokens_used = models.PositiveIntegerField(default=0)

    # Cloudinary URLs (when generated)
    pdf_url = models.URLField(blank=True)
    cover_url = models.URLField(blank=True)

    # File storage (when generated)
    pdf_file = models.FileField(upload_to='books/pdfs/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='books/covers/', null=True, blank=True)

    # User actions
    is_previewed = models.BooleanField(default=False)
    is_downloaded = models.BooleanField(default=False)
    downloaded_at = models.DateTimeField(null=True, blank=True)

    # Cleanup scheduling
    auto_delete_after = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['auto_delete_after']),
        ]

    def __str__(self):
        return f"Book Request: {self.title} - {self.user.email}"

    def save(self, *args, **kwargs):
        # Set auto-delete date if not set and completed
        if not self.auto_delete_after and self.completed_at:
            # Auto-delete 30 days after completion
            self.auto_delete_after = self.completed_at + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if book should be auto-deleted"""
        if self.auto_delete_after:
            return timezone.now() > self.auto_delete_after
        return False

    @property
    def can_download(self):
        """Check if user can download this book based on subscription"""
        if not self.user.profile.subscription_plan:
            return False
        return self.user.profile.subscription_plan.book_limit_per_month > 0 and self.status == 'completed'


class UserGenerationStats(models.Model):
    """Track user generation statistics and limits"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generation_stats')
    books_generated_this_month = models.PositiveIntegerField(default=0)
    total_books_generated = models.PositiveIntegerField(default=0)
    last_generation_at = models.DateTimeField(null=True, blank=True)

    # Monthly reset tracking
    month_start = models.DateField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stats for {self.user.email}"

    def can_generate_book(self):
        """Check if user can generate another book this month"""
        if not self.user.subscription_plan:
            return False

        plan = self.user.subscription_plan
        return self.books_generated_this_month < plan.monthly_book_limit

    def increment_generation_count(self):
        """Increment generation counters"""
        self.books_generated_this_month += 1
        self.total_books_generated += 1
        self.last_generation_at = timezone.now()
        self.save()

    def reset_monthly_count(self):
        """Reset monthly generation count (call on month change)"""
        self.books_generated_this_month = 0
        self.month_start = timezone.now().date()
        self.save()