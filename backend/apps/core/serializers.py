"""
Enhanced Serializers for Domain, Niche, and Audience with domain-specific audiences
"""

from rest_framework import serializers
from .models import DomainModel, NicheModel, AudienceModel


class DomainSerializer(serializers.Serializer):
    """Enhanced Serializer for Domain model"""
    
    id = serializers.CharField(source='_id', read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    icon = serializers.CharField(max_length=10, default='📚')
    is_active = serializers.BooleanField(default=True)
    subscription_tiers = serializers.ListField(
        child=serializers.CharField(),
        default=['personal', 'creator', 'professional', 'entrepreneur', 'enterprise']
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate_name(self, value):
        """Validate domain name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Domain name must be at least 2 characters long")
        return value.strip()
    
    def validate_description(self, value):
        """Validate domain description"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Domain description must be at least 10 characters long")
        return value.strip()
    
    def validate_subscription_tiers(self, value):
        """Validate subscription tiers"""
        valid_tiers = ['personal', 'creator', 'professional', 'entrepreneur', 'enterprise']
        for tier in value:
            if tier not in valid_tiers:
                raise serializers.ValidationError(f"Invalid subscription tier: {tier}")
        return value
    
    def create(self, validated_data):
        """Create domain instance"""
        return DomainModel(**validated_data)
    
    def update(self, instance, validated_data):
        """Update domain instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class NicheSerializer(serializers.Serializer):
    """Enhanced Serializer for Niche model"""
    
    id = serializers.CharField(source='_id', read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    domain_id = serializers.CharField()
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate_name(self, value):
        """Validate niche name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Niche name must be at least 2 characters long")
        return value.strip()
    
    def validate_domain_id(self, value):
        """Validate domain ID format"""
        import re
        if not re.match(r'^[a-f\d]{24}$', value):
            raise serializers.ValidationError("Invalid domain ID format")
        return value
    
    def create(self, validated_data):
        """Create niche instance"""
        return NicheModel(**validated_data)
    
    def update(self, instance, validated_data):
        """Update niche instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class AudienceSerializer(serializers.Serializer):
    """Enhanced Serializer for Audience model with domain-specific targeting"""
    
    id = serializers.CharField(source='_id', read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    domain_id = serializers.CharField()  # Now linked to domain
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate_name(self, value):
        """Validate audience name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Audience name must be at least 2 characters long")
        return value.strip()
    
    def validate_domain_id(self, value):
        """Validate domain ID format"""
        import re
        if not re.match(r'^[a-f\d]{24}$', value):
            raise serializers.ValidationError("Invalid domain ID format")
        return value
    
    def create(self, validated_data):
        """Create audience instance"""
        return AudienceModel(**validated_data)
    
    def update(self, instance, validated_data):
        """Update audience instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class DomainDetailSerializer(serializers.Serializer):
    """Serializer for complete domain details including niches and audiences"""
    
    domain = DomainSerializer()
    niches = NicheSerializer(many=True)
    audiences = AudienceSerializer(many=True)
    stats = serializers.DictField()


class UserDomainsSerializer(serializers.Serializer):
    """Serializer for user-accessible domains with enrichment"""
    
    domains = serializers.ListField(child=serializers.DictField())
    user_tier = serializers.CharField()
    total_count = serializers.IntegerField()
