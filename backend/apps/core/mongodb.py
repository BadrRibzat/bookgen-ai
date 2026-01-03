"""
Enhanced MongoDB utility functions with better error handling and connection management
"""

from django.conf import settings
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure, DuplicateKeyError
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Collection Names
COLLECTIONS = {
    'DOMAINS': 'domains',
    'NICHES': 'niches', 
    'AUDIENCES': 'audiences',
    'BOOKS': 'books',
    'CHAPTERS': 'chapters',
    'BOOK_GENERATION_JOBS': 'book_generation_jobs',
    'USER_ANALYTICS': 'user_analytics',
}

class MongoDBConnection:
    """Singleton MongoDB connection manager"""
    
    _client = None
    _db = None
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                # Use the connection from settings
                if settings.MONGODB_CLIENT:
                    cls._client = settings.MONGODB_CLIENT
                    logger.info("✅ Using MongoDB connection from settings")
                else:
                    logger.error("❌ MongoDB client not available in settings")
                    return None
            except Exception as e:
                logger.error(f"❌ MongoDB connection failed: {e}")
                return None
        return cls._client
    
    @classmethod
    def get_database(cls):
        if cls._db is None:
            client = cls.get_client()
            if client:
                cls._db = settings.MONGODB_DATABASE
            else:
                logger.error("❌ Cannot get database - no MongoDB client")
        return cls._db
    
    @classmethod
    def close_connection(cls):
        # Don't close the connection as it's managed by settings
        pass

def get_database():
    """Get database instance"""
    return MongoDBConnection.get_database()

def get_collection(collection_name):
    """Get collection with validation"""
    if collection_name not in COLLECTIONS.values():
        raise ValueError(f"Invalid collection name: {collection_name}")
    
    db = get_database()
    if db is None:
        raise ConnectionError("MongoDB database is not available")
    
    return db[collection_name]

# Enhanced CRUD Operations with proper error handling
def insert_one(collection_name, document):
    """Insert a single document with enhanced error handling"""
    try:
        collection = get_collection(collection_name)
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()
        result = collection.insert_one(document)
        logger.debug(f"Inserted document into {collection_name}: {result.inserted_id}")
        return str(result.inserted_id)
    except DuplicateKeyError as e:
        logger.error(f"Duplicate key error in {collection_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inserting into {collection_name}: {e}")
        raise

def insert_many(collection_name, documents):
    """Insert multiple documents with batch processing"""
    try:
        collection = get_collection(collection_name)
        now = datetime.utcnow()
        for doc in documents:
            doc['created_at'] = now
            doc['updated_at'] = now
        
        result = collection.insert_many(documents, ordered=False)
        logger.info(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
        return [str(id) for id in result.inserted_ids]
    except Exception as e:
        logger.error(f"Error bulk inserting into {collection_name}: {e}")
        raise

def find_one(collection_name, query, projection=None):
    """Find single document with ID conversion"""
    try:
        collection = get_collection(collection_name)
        
        # Convert string IDs to ObjectId if needed
        if '_id' in query and isinstance(query['_id'], str):
            try:
                query['_id'] = ObjectId(query['_id'])
            except InvalidId:
                return None
        
        document = collection.find_one(query, projection)
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    except Exception as e:
        logger.error(f"Error finding document in {collection_name}: {e}")
        return None

def find_many(collection_name, query=None, projection=None, limit=0, skip=0, sort=None):
    """Find multiple documents with pagination support"""
    try:
        collection = get_collection(collection_name)
        
        if query is None:
            query = {}
        
        # Handle ID conversion in query
        if '_id' in query and isinstance(query['_id'], str):
            try:
                query['_id'] = ObjectId(query['_id'])
            except InvalidId:
                return []
        
        cursor = collection.find(query, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        documents = list(cursor)
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        return documents
    except Exception as e:
        logger.error(f"Error finding documents in {collection_name}: {e}")
        return []

def update_one(collection_name, query, update_data, upsert=False):
    """Update single document with timestamp"""
    try:
        collection = get_collection(collection_name)
        
        # Convert string ID to ObjectId if needed
        if '_id' in query and isinstance(query['_id'], str):
            try:
                query['_id'] = ObjectId(query['_id'])
            except InvalidId:
                return 0
        
        # Ensure updated_at is set
        if '$set' in update_data:
            update_data['$set']['updated_at'] = datetime.utcnow()
        else:
            update_data = {'$set': {**update_data, 'updated_at': datetime.utcnow()}}
        
        result = collection.update_one(query, update_data, upsert=upsert)
        return result.modified_count
    except Exception as e:
        logger.error(f"Error updating document in {collection_name}: {e}")
        return 0

def delete_one(collection_name, query):
    """Delete single document"""
    try:
        collection = get_collection(collection_name)
        
        if '_id' in query and isinstance(query['_id'], str):
            try:
                query['_id'] = ObjectId(query['_id'])
            except InvalidId:
                return 0
        
        result = collection.delete_one(query)
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting document from {collection_name}: {e}")
        return 0

def delete_many(collection_name, query):
    """Delete multiple documents"""
    try:
        collection = get_collection(collection_name)
        
        # Handle ID conversion in query
        if '_id' in query and isinstance(query['_id'], str):
            try:
                query['_id'] = ObjectId(query['_id'])
            except InvalidId:
                return 0
        
        result = collection.delete_many(query)
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error bulk deleting from {collection_name}: {e}")
        return 0

def count_documents(collection_name, query=None):
    """Count documents matching query"""
    try:
        collection = get_collection(collection_name)
        if query is None:
            query = {}
        return collection.count_documents(query)
    except Exception as e:
        logger.error(f"Error counting documents in {collection_name}: {e}")
        return 0

def aggregate(collection_name, pipeline):
    """Run aggregation pipeline"""
    try:
        collection = get_collection(collection_name)
        result = list(collection.aggregate(pipeline))
        
        # Convert ObjectIds to strings
        for doc in result:
            if '_id' in doc and isinstance(doc['_id'], ObjectId):
                doc['_id'] = str(doc['_id'])
        
        return result
    except Exception as e:
        logger.error(f"Error in aggregation pipeline for {collection_name}: {e}")
        return []

# Helper functions
def to_object_id(id_string):
    """Safely convert string to ObjectId"""
    try:
        return ObjectId(id_string) if id_string else None
    except (InvalidId, TypeError):
        return None

def is_valid_object_id(id_string):
    """Check if string is valid ObjectId"""
    try:
        ObjectId(id_string)
        return True
    except (InvalidId, TypeError):
        return False

# Index Management
def create_indexes():
    """Create necessary indexes for optimal performance"""
    try:
        # Domain indexes
        get_collection('domains').create_index([('name', ASCENDING)], unique=True)
        get_collection('domains').create_index([('subscription_tiers', ASCENDING)])
        get_collection('domains').create_index([('is_active', ASCENDING)])
        
        # Niche indexes
        get_collection('niches').create_index([('domain_id', ASCENDING), ('name', ASCENDING)], unique=True)
        get_collection('niches').create_index([('is_active', ASCENDING)])
        
        # Audience indexes  
        get_collection('audiences').create_index([('domain_id', ASCENDING), ('name', ASCENDING)], unique=True)
        get_collection('audiences').create_index([('is_active', ASCENDING)])
        
        logger.info("✅ MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# Initialize indexes when module loads
try:
    create_indexes()
except Exception as e:
    logger.warning(f"Could not create indexes on startup: {e}")
