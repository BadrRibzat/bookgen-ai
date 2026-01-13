from rest_framework import serializers
from django.utils import timezone
from .models import Domain, BookGenerationRequest, UserGenerationStats
from apps.core.services import DomainService, NicheService


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
    domain_name = serializers.CharField(source='domain_name', read_only=True)
    domain_color = serializers.SerializerMethodField()

    class Meta:
        model = BookGenerationRequest
        fields = [
            'id', 'title', 'domain_name', 'domain_color', 'status',
            'is_downloaded', 'created_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'is_expired']

    def get_domain_color(self, obj):
        """Get domain color from MongoDB"""
        from apps.core.services import DomainService
        domain = DomainService.get_domain_by_id(obj.domain_id)
        return domain.get('color', '#3B82F6') if domain else '#3B82F6'


class BookGenerationRequestDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed book generation request view"""
    domain = serializers.SerializerMethodField()
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

    def get_domain(self, obj):
        """Get domain details from MongoDB"""
        from apps.core.services import DomainService
        domain = DomainService.get_domain_by_id(obj.domain_id)
        if domain:
            return {
                'id': str(domain.get('_id')),
                'name': domain.get('name'),
                'display_name': domain.get('display_name'),
                'description': domain.get('description'),
                'icon': domain.get('icon'),
                'color': domain.get('color'),
                'is_active': domain.get('is_active')
            }
        return None


class BookGenerationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating book generation requests"""
    domain_id = serializers.CharField(write_only=True)
    niche_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = BookGenerationRequest
        fields = [
            'domain_id', 'niche_id', 'title', 'target_word_count', 'cover_option'
        ]

    def validate_domain_id(self, value):
        """Validate domain exists and is active"""
        domain = DomainService.get_domain_by_id(value)
        if not domain:
            raise serializers.ValidationError("Domain not found or inactive.")
        return domain

    def validate_niche_id(self, value):
        """Validate niche exists and belongs to the domain"""
        if not value:
            return None
        # We'll validate this in the main validate method after we have the domain
        return value

    def validate_target_word_count(self, value):
        """Validate target word count based on user subscription"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'profile') and user.profile.subscription_plan:
                max_words = user.profile.subscription_plan.max_words_per_book
                if value > max_words:
                    raise serializers.ValidationError(
                        f"Word count cannot exceed {max_words} for your subscription plan."
                    )
        return value

    def validate(self, data):
        """Validate generation request"""
        user = self.context['request'].user
        domain = data.get('domain_id')
        niche_id = data.get('niche_id')

        # Check if user can generate books
        if hasattr(user, 'generation_stats'):
            if not user.generation_stats.can_generate_book():
                raise serializers.ValidationError(
                    "You have reached your monthly book generation limit."
                )

        # Check if domain is active (already validated in validate_domain_id)
        if not domain.get('is_active', False):
            raise serializers.ValidationError("This domain is not currently available.")

        # Validate niche if provided
        if niche_id:
            from apps.core.services import NicheService
            niche = NicheService.get_niche_by_id(niche_id)
            if not niche or niche.get('domain_id') != domain.get('_id'):
                raise serializers.ValidationError("Invalid niche for this domain.")
            # Set custom_prompt to niche description
            data['custom_prompt'] = niche.get('description', '')

        # Set domain fields
        data['domain_id'] = str(domain.get('_id'))
        data['domain_name'] = domain.get('display_name', domain.get('name', ''))

        return data

    def create(self, validated_data):
        """Create book generation request, excluding niche_id from model creation"""
        # Remove niche_id as it's not a model field, used only for validation
        validated_data.pop('niche_id', None)
        return super().create(validated_data)


class UserGenerationStatsSerializer(serializers.ModelSerializer):
    """Serializer for user generation statistics"""
    remaining_generations = serializers.SerializerMethodField()
    plan_name = serializers.CharField(source='user.profile.subscription_plan.name', read_only=True)
    monthly_limit = serializers.IntegerField(source='user.profile.subscription_plan.monthly_book_limit', read_only=True)

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
        if hasattr(obj.user, 'profile') and obj.user.profile.subscription_plan:
            return max(0, obj.user.profile.subscription_plan.monthly_book_limit - obj.books_generated_this_month)
        return 0