"""
Enhanced business logic services with proper error handling and MongoDB integration
"""

from typing import List, Optional, Dict, Any
from django.conf import settings
from .mongodb import (
    get_collection, find_many, find_one, insert_one, insert_many,
    update_one, delete_one, count_documents, to_object_id,
    COLLECTIONS
)
from .models import DomainModel, NicheModel, AudienceModel
import logging

logger = logging.getLogger(__name__)


class DomainService:
    """Enhanced Domain service with comprehensive business logic"""
    
    @staticmethod
    def get_all_domains(user_tier: str = 'personal') -> List[Dict[str, Any]]:
        """
        Get all active domains accessible by user's subscription tier
        
        Args:
            user_tier: User's subscription tier
        
        Returns:
            List of domain documents
        """
        try:
            query = {
                'is_active': True,
                'subscription_tiers': user_tier
            }
            
            domains = find_many(
                COLLECTIONS['DOMAINS'],
                query,
                sort=[('name', 1)]
            )
            
            logger.info(f"Retrieved {len(domains)} domains for tier: {user_tier}")
            return domains
            
        except Exception as e:
            logger.error(f"Error retrieving domains for tier {user_tier}: {e}")
            return []
    
    @staticmethod
    def get_domain_by_id(domain_id: str) -> Optional[Dict[str, Any]]:
        """Get domain by ID with validation"""
        try:
            if not domain_id:
                logger.warning("Domain ID is required")
                return None
            
            domain = find_one(COLLECTIONS['DOMAINS'], {'_id': domain_id})
            if not domain:
                logger.warning(f"Domain not found: {domain_id}")
                return None
            
            return domain
            
        except Exception as e:
            logger.error(f"Error retrieving domain {domain_id}: {e}")
            return None
    
    @staticmethod
    def get_domains_by_tiers(subscription_tiers: List[str]) -> List[Dict[str, Any]]:
        """Get domains accessible by multiple subscription tiers"""
        try:
            query = {
                'is_active': True,
                'subscription_tiers': {'$in': subscription_tiers}
            }
            
            domains = find_many(
                COLLECTIONS['DOMAINS'],
                query,
                sort=[('name', 1)]
            )
            
            return domains
            
        except Exception as e:
            logger.error(f"Error retrieving domains for tiers {subscription_tiers}: {e}")
            return []
    
    @staticmethod
    def create_domain(domain_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new domain with validation
        
        Args:
            domain_data: Domain information
        
        Returns:
            Created domain ID or None if failed
        """
        try:
            # Create and validate domain model
            domain = DomainModel(**domain_data)
            domain.validate()
            
            # Check for duplicate domain name
            existing = find_one(COLLECTIONS['DOMAINS'], {'name': domain.name})
            if existing:
                raise ValueError(f"Domain with name '{domain.name}' already exists")
            
            # Insert into database
            domain_id = insert_one(COLLECTIONS['DOMAINS'], domain.to_dict())
            
            logger.info(f"Created domain: {domain.name} (ID: {domain_id})")
            return domain_id
            
        except ValueError as e:
            logger.warning(f"Domain validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating domain: {e}")
            return None
    
    @staticmethod
    def update_domain(domain_id: str, update_data: Dict[str, Any]) -> bool:
        """Update domain information"""
        try:
            # Validate domain exists
            domain = DomainService.get_domain_by_id(domain_id)
            if not domain:
                return False
            
            # Update domain
            modified_count = update_one(
                COLLECTIONS['DOMAINS'],
                {'_id': domain_id},
                update_data
            )
            
            success = modified_count > 0
            if success:
                logger.info(f"Updated domain: {domain_id}")
            else:
                logger.warning(f"No changes made to domain: {domain_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating domain {domain_id}: {e}")
            return False
    
    @staticmethod
    def delete_domain(domain_id: str) -> bool:
        """Soft delete domain (set inactive)"""
        try:
            modified_count = update_one(
                COLLECTIONS['DOMAINS'],
                {'_id': domain_id},
                {'is_active': False}
            )
            
            success = modified_count > 0
            if success:
                logger.info(f"Soft deleted domain: {domain_id}")
            else:
                logger.warning(f"Domain not found or already inactive: {domain_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting domain {domain_id}: {e}")
            return False


class NicheService:
    """Enhanced Niche service with domain relationship management"""
    
    @staticmethod
    def get_niches_by_domain(domain_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all niches for a domain
        
        Args:
            domain_id: Domain ID
            active_only: Only return active niches
        
        Returns:
            List of niche documents
        """
        try:
            query = {'domain_id': domain_id}
            if active_only:
                query['is_active'] = True
            
            niches = find_many(
                COLLECTIONS['NICHES'],
                query,
                sort=[('name', 1)]
            )
            
            logger.debug(f"Retrieved {len(niches)} niches for domain: {domain_id}")
            return niches
            
        except Exception as e:
            logger.error(f"Error retrieving niches for domain {domain_id}: {e}")
            return []
    
    @staticmethod
    def get_niche_by_id(niche_id: str) -> Optional[Dict[str, Any]]:
        """Get niche by ID"""
        try:
            if not niche_id:
                return None
            
            niche = find_one(COLLECTIONS['NICHES'], {'_id': niche_id})
            return niche
            
        except Exception as e:
            logger.error(f"Error retrieving niche {niche_id}: {e}")
            return None
    
    @staticmethod
    def get_niches_by_domain_name(domain_name: str) -> List[Dict[str, Any]]:
        """Get niches by domain name (convenience method)"""
        try:
            # First get domain by name
            domain = find_one(COLLECTIONS['DOMAINS'], {'name': domain_name})
            if not domain:
                return []
            
            # Then get niches for that domain
            return NicheService.get_niches_by_domain(str(domain['_id']))
            
        except Exception as e:
            logger.error(f"Error retrieving niches for domain name {domain_name}: {e}")
            return []
    
    @staticmethod
    def create_niche(niche_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new niche with validation
        
        Args:
            niche_data: Niche information
        
        Returns:
            Created niche ID or None if failed
        """
        try:
            # Create and validate niche model
            niche = NicheModel(**niche_data)
            niche.validate()
            
            # Verify domain exists
            domain = DomainService.get_domain_by_id(niche.domain_id)
            if not domain:
                raise ValueError(f"Domain not found: {niche.domain_id}")
            
            # Check for duplicate niche name in same domain
            existing = find_one(
                COLLECTIONS['NICHES'],
                {'name': niche.name, 'domain_id': niche.domain_id}
            )
            if existing:
                raise ValueError(f"Niche '{niche.name}' already exists in this domain")
            
            # Insert into database
            niche_id = insert_one(COLLECTIONS['NICHES'], niche.to_dict())
            
            logger.info(f"Created niche: {niche.name} (Domain: {domain['name']})")
            return niche_id
            
        except ValueError as e:
            logger.warning(f"Niche validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating niche: {e}")
            return None
    
    @staticmethod
    def create_niches_bulk(niches_data: List[Dict[str, Any]]) -> List[str]:
        """Create multiple niches with batch validation"""
        try:
            valid_niches = []
            
            for niche_data in niches_data:
                try:
                    niche = NicheModel(**niche_data)
                    niche.validate()
                    
                    # Verify domain exists
                    domain = DomainService.get_domain_by_id(niche.domain_id)
                    if not domain:
                        logger.warning(f"Skipping niche '{niche.name}': Domain not found")
                        continue
                    
                    valid_niches.append(niche.to_dict())
                    
                except ValueError as e:
                    logger.warning(f"Skipping invalid niche data: {e}")
                    continue
            
            if valid_niches:
                niche_ids = insert_many(COLLECTIONS['NICHES'], valid_niches)
                logger.info(f"Created {len(niche_ids)} niches in bulk")
                return niche_ids
            else:
                logger.warning("No valid niches to create")
                return []
                
        except Exception as e:
            logger.error(f"Error in bulk niche creation: {e}")
            return []


class AudienceService:
    """Enhanced Audience service with domain-specific targeting"""
    
    @staticmethod
    def get_audiences_by_domain(domain_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all audiences for a domain
        
        Args:
            domain_id: Domain ID
            active_only: Only return active audiences
        
        Returns:
            List of audience documents
        """
        try:
            query = {'domain_id': domain_id}
            if active_only:
                query['is_active'] = True
            
            audiences = find_many(
                COLLECTIONS['AUDIENCES'],
                query,
                sort=[('name', 1)]
            )
            
            logger.debug(f"Retrieved {len(audiences)} audiences for domain: {domain_id}")
            return audiences
            
        except Exception as e:
            logger.error(f"Error retrieving audiences for domain {domain_id}: {e}")
            return []
    
    @staticmethod
    def get_audience_by_id(audience_id: str) -> Optional[Dict[str, Any]]:
        """Get audience by ID"""
        try:
            if not audience_id:
                return None
            
            audience = find_one(COLLECTIONS['AUDIENCES'], {'_id': audience_id})
            return audience
            
        except Exception as e:
            logger.error(f"Error retrieving audience {audience_id}: {e}")
            return None
    
    @staticmethod
    def create_audience(audience_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new audience with validation
        
        Args:
            audience_data: Audience information
        
        Returns:
            Created audience ID or None if failed
        """
        try:
            # Create and validate audience model
            audience = AudienceModel(**audience_data)
            audience.validate()
            
            # Verify domain exists
            domain = DomainService.get_domain_by_id(audience.domain_id)
            if not domain:
                raise ValueError(f"Domain not found: {audience.domain_id}")
            
            # Check for duplicate audience name in same domain
            existing = find_one(
                COLLECTIONS['AUDIENCES'],
                {'name': audience.name, 'domain_id': audience.domain_id}
            )
            if existing:
                raise ValueError(f"Audience '{audience.name}' already exists in this domain")
            
            # Insert into database
            audience_id = insert_one(COLLECTIONS['AUDIENCES'], audience.to_dict())
            
            logger.info(f"Created audience: {audience.name} (Domain: {domain['name']})")
            return audience_id
            
        except ValueError as e:
            logger.warning(f"Audience validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating audience: {e}")
            return None
    
    @staticmethod
    def create_audiences_bulk(audiences_data: List[Dict[str, Any]]) -> List[str]:
        """Create multiple audiences with batch validation"""
        try:
            valid_audiences = []
            
            for audience_data in audiences_data:
                try:
                    audience = AudienceModel(**audience_data)
                    audience.validate()
                    
                    # Verify domain exists
                    domain = DomainService.get_domain_by_id(audience.domain_id)
                    if not domain:
                        logger.warning(f"Skipping audience '{audience.name}': Domain not found")
                        continue
                    
                    valid_audiences.append(audience.to_dict())
                    
                except ValueError as e:
                    logger.warning(f"Skipping invalid audience data: {e}")
                    continue
            
            if valid_audiences:
                audience_ids = insert_many(COLLECTIONS['AUDIENCES'], valid_audiences)
                logger.info(f"Created {len(audience_ids)} audiences in bulk")
                return audience_ids
            else:
                logger.warning("No valid audiences to create")
                return []
                
        except Exception as e:
            logger.error(f"Error in bulk audience creation: {e}")
            return []
    
    @staticmethod
    def get_all_domain_audiences(domain_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get audiences for multiple domains
        
        Args:
            domain_ids: List of domain IDs
        
        Returns:
            Dictionary mapping domain_id to list of audiences
        """
        try:
            result = {}
            for domain_id in domain_ids:
                audiences = AudienceService.get_audiences_by_domain(domain_id)
                result[domain_id] = audiences
            return result
        except Exception as e:
            logger.error(f"Error getting audiences for multiple domains: {e}")
            return {}


class DataSeedService:
    """Service for seeding initial data"""
    
    @staticmethod
    def clear_all_data():
        """Clear all domain, niche, and audience data (for reseeding)"""
        try:
            from .mongodb import get_collection
            
            collections = [COLLECTIONS['DOMAINS'], COLLECTIONS['NICHES'], COLLECTIONS['AUDIENCES']]
            for collection_name in collections:
                collection = get_collection(collection_name)
                collection.delete_many({})
            
            logger.info("Cleared all domain, niche, and audience data")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return False
    
    @staticmethod
    def get_data_counts() -> Dict[str, int]:
        """Get counts of current data"""
        try:
            return {
                'domains': count_documents(COLLECTIONS['DOMAINS'], {}),
                'niches': count_documents(COLLECTIONS['NICHES'], {}),
                'audiences': count_documents(COLLECTIONS['AUDIENCES'], {}),
            }
        except Exception as e:
            logger.error(f"Error getting data counts: {e}")
            return {'domains': 0, 'niches': 0, 'audiences': 0}
