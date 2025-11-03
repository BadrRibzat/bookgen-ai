"""
Enhanced Core models for Domain, Niche, and Audience
These are stored in MongoDB via PyMongo (not Django ORM)
This file contains helper classes for data validation and serialization with validation and business logic
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
import re


class BaseModel:
    """Base model with common functionality"""
    
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    def validate(self):
        """Validate model data - to be implemented by subclasses"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB"""
        data = {
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        if self._id:
            data['_id'] = ObjectId(self._id) if isinstance(self._id, str) else self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from MongoDB document"""
        return cls(**data)


class DomainModel(BaseModel):
    """
    Enhanced Domain model with validation
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        icon: str = "📚",
        is_active: bool = True,
        subscription_tiers: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.icon = icon
        self.is_active = is_active
        self.subscription_tiers = subscription_tiers or ['personal', 'creator', 'professional', 'entrepreneur', 'enterprise']
    
    def validate(self):
        """Validate domain data"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Domain name must be at least 2 characters long")
        
        if not self.description or len(self.description.strip()) < 10:
            raise ValueError("Domain description must be at least 10 characters long")
        
        valid_tiers = ['personal', 'creator', 'professional', 'entrepreneur', 'enterprise']
        for tier in self.subscription_tiers:
            if tier not in valid_tiers:
                raise ValueError(f"Invalid subscription tier: {tier}")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name.strip(),
            'description': self.description.strip(),
            'icon': self.icon,
            'is_active': self.is_active,
            'subscription_tiers': self.subscription_tiers,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainModel':
        return cls(
            _id=str(data.get('_id')) if data.get('_id') else None,
            name=data.get('name', ''),
            description=data.get('description', ''),
            icon=data.get('icon', '📚'),
            is_active=data.get('is_active', True),
            subscription_tiers=data.get('subscription_tiers', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )


class NicheModel(BaseModel):
    """
    Enhanced Niche model with validation
    """
    
    def __init__(
        self,
        name: str,
        domain_id: str,
        description: str = "",
        is_active: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.domain_id = domain_id
        self.description = description
        self.is_active = is_active
    
    def validate(self):
        """Validate niche data"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Niche name must be at least 2 characters long")
        
        if not self.domain_id:
            raise ValueError("Domain ID is required")
        
        # Validate domain_id format (should be valid ObjectId string)
        if not re.match(r'^[a-f\d]{24}$', self.domain_id):
            raise ValueError("Invalid domain ID format")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name.strip(),
            'domain_id': self.domain_id,
            'description': self.description.strip(),
            'is_active': self.is_active,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NicheModel':
        return cls(
            _id=str(data.get('_id')) if data.get('_id') else None,
            name=data.get('name', ''),
            domain_id=data.get('domain_id', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )


class AudienceModel(BaseModel):
    """
    Enhanced Audience model with domain-specific targeting
    """
    
    def __init__(
        self,
        name: str,
        domain_id: str,
        description: str = "",
        is_active: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.domain_id = domain_id
        self.description = description
        self.is_active = is_active
    
    def validate(self):
        """Validate audience data"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Audience name must be at least 2 characters long")
        
        if not self.domain_id:
            raise ValueError("Domain ID is required")
        
        if not re.match(r'^[a-f\d]{24}$', self.domain_id):
            raise ValueError("Invalid domain ID format")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name.strip(),
            'domain_id': self.domain_id,
            'description': self.description.strip(),
            'is_active': self.is_active,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudienceModel':
        return cls(
            _id=str(data.get('_id')) if data.get('_id') else None,
            name=data.get('name', ''),
            domain_id=data.get('domain_id', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )
