from rest_framework import serializers
from django.utils import timezone
from .models import Domain, BookGenerationRequest, UserGenerationStats


class DomainSerializer(serializers.ModelSerializer):
    """Serializer for Domain model"""
    class Meta:
        model = Domain
        fields = [
            'id', 'name', 'display_name', 'description',
            'icon', 'color', 'trending_score', 'is_active'
        ]
        read_only_fields = ['id']


class BookGenerationRequestListSerializer(serializers.ModelSerializer):
    """Serializer for listing book generation requests"""
    domain_name = serializers.CharField(source='domain.display_name', read_only=True)
    domain_color = serializers.CharField(source='domain.color', read_only=True)

    class Meta:
        model = BookGenerationRequest
        fields = [
            'id', 'title', 'domain_name', 'domain_color', 'status',
            'is_downloaded', 'created_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'is_expired']


class BookGenerationRequestDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed book generation request view"""
    domain = DomainSerializer(read_only=True)
    can_download = serializers.BooleanField(read_only=True)

    class Meta:
        model = BookGenerationRequest
        fields = [
            'id', 'title', 'domain', 'custom_prompt', 'target_word_count',
            'status', 'started_at', 'completed_at', 'error_message',
            'is_previewed', 'is_downloaded', 'downloaded_at',
            'pdf_url', 'cover_url', 'pdf_file', 'cover_image', 'can_download', 'is_expired',
            'tokens_used', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'started_at', 'completed_at', 'error_message',
            'is_previewed', 'is_downloaded', 'downloaded_at',
            'pdf_url', 'cover_url', 'pdf_file', 'cover_image', 'can_download', 'is_expired',
            'tokens_used', 'created_at'
        ]


class BookGenerationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating book generation requests"""
    class Meta:
        model = BookGenerationRequest
        fields = [
            'domain', 'title', 'custom_prompt', 'target_word_count'
        ]

    def validate_target_word_count(self, value):
        """Validate target word count based on user subscription"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.subscription_plan:
                max_words = user.subscription_plan.max_words_per_book
                if value > max_words:
                    raise serializers.ValidationError(
                        f"Word count cannot exceed {max_words} for your subscription plan."
                    )
        return value

    def validate(self, data):
        """Validate generation request"""
        user = self.context['request'].user

        # Check if user can generate books
        if hasattr(user, 'generation_stats'):
            if not user.generation_stats.can_generate_book():
                raise serializers.ValidationError(
                    "You have reached your monthly book generation limit."
                )

        # Check if domain is active
        domain = data['domain']
        if not domain.is_active:
            raise serializers.ValidationError("This domain is not currently available.")

        return data


class UserGenerationStatsSerializer(serializers.ModelSerializer):
    """Serializer for user generation statistics"""
    remaining_generations = serializers.SerializerMethodField()
    plan_name = serializers.CharField(source='user.subscription_plan.name', read_only=True)
    monthly_limit = serializers.IntegerField(source='user.subscription_plan.monthly_book_limit', read_only=True)

    class Meta:
        model = UserGenerationStats
        fields = [
            'books_generated_this_month', 'total_books_generated',
            'remaining_generations', 'plan_name', 'monthly_limit',
            'last_generation_at', 'month_start'
        ]
        read_only_fields = ['books_generated_this_month', 'total_books_generated',
                          'remaining_generations', 'last_generation_at', 'month_start']

    def get_remaining_generations(self, obj):
        """Calculate remaining generations for current month"""
        if obj.user.subscription_plan:
            return max(0, obj.user.subscription_plan.monthly_book_limit - obj.books_generated_this_month)
        return 0