"""
Enhanced API Views with proper error handling and domain-specific audiences
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from .services import DomainService, NicheService, AudienceService
from .serializers import DomainSerializer, NicheSerializer, AudienceSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_domains(request):
    """
    Get all domains accessible by user's subscription tier
    GET /api/domains/
    """
    try:
        # Get user's subscription tier (default to personal for anonymous)
        user_tier = 'personal'
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            # Get plan name from ForeignKey
            plan_name = request.user.profile.subscription_plan.name.lower() if request.user.profile.subscription_plan else 'free'
            
            # Map frontend subscription tiers to domain subscription tiers
            tier_mapping = {
                'free': 'personal',
                'pro': 'creator', 
                'enterprise': 'enterprise'
            }
            user_tier = tier_mapping.get(plan_name, plan_name)
        
        # Generate cache key
        cache_key = f"domains_{user_tier}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Returning cached domains for tier: {user_tier}")
            return Response(cached_data)
        
        domains = DomainService.get_all_domains(user_tier)
        serializer = DomainSerializer(domains, many=True)
        
        response_data = {
            'success': True,
            'domains': serializer.data,
            'count': len(serializer.data),
            'user_tier': user_tier
        }
        
        # Cache for 1 hour
        cache.set(cache_key, response_data, 60 * 60)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching domains: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to fetch domains.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_domain_niches(request, domain_id):
    """
    Get all niches for a specific domain
    GET /api/domains/{domain_id}/niches/
    """
    try:
        # Generate cache key
        cache_key = f"domain_{domain_id}_niches"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Returning cached niches for domain: {domain_id}")
            return Response(cached_data)
        
        # Verify domain exists and get domain info
        domain = DomainService.get_domain_by_id(domain_id)
        if not domain:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Domain not found.',
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get niches for domain
        niches = NicheService.get_niches_by_domain(domain_id)
        niche_serializer = NicheSerializer(niches, many=True)
        domain_serializer = DomainSerializer(domain)
        
        response_data = {
            'success': True,
            'niches': niche_serializer.data,
            'domain': domain_serializer.data,
            'count': len(niche_serializer.data)
        }
        
        # Cache for 1 hour
        cache.set(cache_key, response_data, 60 * 60)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching niches for domain {domain_id}: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to fetch niches.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_domain_audiences(request, domain_id):
    """
    Get all audiences for a specific domain
    GET /api/domains/{domain_id}/audiences/
    """
    try:
        # Generate cache key
        cache_key = f"domain_{domain_id}_audiences"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Returning cached audiences for domain: {domain_id}")
            return Response(cached_data)
        
        # Verify domain exists and get domain info
        domain = DomainService.get_domain_by_id(domain_id)
        if not domain:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Domain not found.',
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get audiences for domain
        audiences = AudienceService.get_audiences_by_domain(domain_id)
        audience_serializer = AudienceSerializer(audiences, many=True)
        domain_serializer = DomainSerializer(domain)
        
        response_data = {
            'success': True,
            'audiences': audience_serializer.data,
            'domain': domain_serializer.data,
            'count': len(audience_serializer.data)
        }
        
        # Cache for 1 hour
        cache.set(cache_key, response_data, 60 * 60)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching audiences for domain {domain_id}: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to fetch audiences.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_domain_details(request, domain_id):
    """
    Get complete domain details including niches and audiences
    GET /api/domains/{domain_id}/details/
    """
    try:
        cache_key = f"domain_{domain_id}_details"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get domain
        domain = DomainService.get_domain_by_id(domain_id)
        if not domain:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Domain not found.',
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get niches and audiences
        niches = NicheService.get_niches_by_domain(domain_id)
        audiences = AudienceService.get_audiences_by_domain(domain_id)
        
        # Serialize data
        domain_serializer = DomainSerializer(domain)
        niche_serializer = NicheSerializer(niches, many=True)
        audience_serializer = AudienceSerializer(audiences, many=True)
        
        response_data = {
            'success': True,
            'domain': domain_serializer.data,
            'niches': niche_serializer.data,
            'audiences': audience_serializer.data,
            'stats': {
                'niches_count': len(niches),
                'audiences_count': len(audiences)
            }
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, response_data, 60 * 30)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching domain details {domain_id}: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to fetch domain details.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_accessible_domains(request):
    """
    Get all domains accessible by authenticated user with complete details
    GET /api/user/domains/
    """
    try:
        user = request.user
        
        # Admin users get access to all domains
        if user.is_staff or user.is_superuser:
            user_tier = 'enterprise'  # Highest tier for admins
        elif hasattr(user, 'profile') and user.profile.subscription_plan:
            user_tier = user.profile.subscription_plan.name.lower()
        else:
            user_tier = 'free'
        
        # Map to domain tier
        tier_mapping = {
            'free': 'personal',
            'pro': 'creator', 
            'enterprise': 'enterprise'
        }
        user_tier = tier_mapping.get(user_tier, user_tier)
        
        cache_key = f"user_{user.id}_domains"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get accessible domains
        domains = DomainService.get_all_domains(user_tier)
        
        # Enrich with niches and audiences
        enriched_domains = []
        for domain in domains:
            domain_id = str(domain['_id'])
            niches = NicheService.get_niches_by_domain(domain_id)
            audiences = AudienceService.get_audiences_by_domain(domain_id)
            
            enriched_domains.append({
                **domain,
                'id': domain_id,
                'niches_count': len(niches),
                'audiences_count': len(audiences),
                'niches_sample': [
                    {**niche, 'id': str(niche['_id'])} for niche in niches[:3]
                ],
                'audiences_sample': [
                    {**audience, 'id': str(audience['_id'])} for audience in audiences[:3]
                ]
            })
        
        response_data = {
            'success': True,
            'domains': enriched_domains,
            'user_tier': user_tier,
            'total_count': len(enriched_domains)
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching user domains: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to fetch user domains.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cache(request):
    """
    Clear cache for domains, niches, and audiences
    POST /api/cache/clear/
    """
    try:
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Only staff users can clear cache.',
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Clear all domain-related cache
        from django.core.cache import cache
        cache.delete_many(['domains_personal', 'domains_creator', 'domains_professional', 'domains_entrepreneur', 'domains_enterprise'])
        
        # Clear pattern-based cache keys
        cache.delete_pattern('domain_*')
        cache.delete_pattern('user_*_domains')
        
        logger.info("Cache cleared by staff user")
        
        return Response({
            'success': True,
            'message': 'Cache cleared successfully.',
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': 'CACHE_ERROR',
                'message': 'Failed to clear cache.',
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
