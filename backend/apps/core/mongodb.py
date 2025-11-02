"""
MongoDB utility functions
Provides easy access to MongoDB collections and common operations
"""

from django.conf import settings
from pymongo.errors import ConnectionFailure, OperationFailure
from bson.objectid import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_mongodb_database():
    """Get MongoDB database instance"""
    if settings.MONGODB_DATABASE is None:
        raise ConnectionFailure("MongoDB is not connected")
    return settings.MONGODB_DATABASE


def get_collection(collection_name):
    """
    Get a MongoDB collection by name
    
    Args:
        collection_name (str): Name of the collection
    
    Returns:
        Collection: PyMongo collection object
    """
    db = get_mongodb_database()
    return db[collection_name]


# ============================================
# Collection Names (Constants)
# ============================================
COLLECTIONS = {
    'DOMAINS': 'domains',
    'NICHES': 'niches',
    'AUDIENCES': 'audiences',
    'BOOKS': 'books',
    'BOOK_CHAPTERS': 'book_chapters',
    'USER_ANALYTICS': 'user_analytics',
}


# ============================================
# Common MongoDB Operations
# ============================================

def insert_one(collection_name, document):
    """Insert a single document"""
    try:
        collection = get_collection(collection_name)
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting document: {e}")
        raise


def insert_many(collection_name, documents):
    """Insert multiple documents"""
    try:
        collection = get_collection(collection_name)
        now = datetime.utcnow()
        for doc in documents:
            doc['created_at'] = now
            doc['updated_at'] = now
        result = collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    except Exception as e:
        logger.error(f"Error inserting documents: {e}")
        raise


def find_one(collection_name, query, projection=None):
    """Find a single document"""
    try:
        collection = get_collection(collection_name)
        document = collection.find_one(query, projection)
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    except Exception as e:
        logger.error(f"Error finding document: {e}")
        raise


def find_many(collection_name, query, projection=None, limit=None, skip=None, sort=None):
    """Find multiple documents"""
    try:
        collection = get_collection(collection_name)
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
        logger.error(f"Error finding documents: {e}")
        raise


def update_one(collection_name, query, update, upsert=False):
    """Update a single document"""
    try:
        collection = get_collection(collection_name)
        if '$set' in update:
            update['$set']['updated_at'] = datetime.utcnow()
        else:
            update = {'$set': {**update, 'updated_at': datetime.utcnow()}}
        
        result = collection.update_one(query, update, upsert=upsert)
        return result.modified_count
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise


def update_many(collection_name, query, update):
    """Update multiple documents"""
    try:
        collection = get_collection(collection_name)
        if '$set' in update:
            update['$set']['updated_at'] = datetime.utcnow()
        else:
            update = {'$set': {**update, 'updated_at': datetime.utcnow()}}
        
        result = collection.update_many(query, update)
        return result.modified_count
    except Exception as e:
        logger.error(f"Error updating documents: {e}")
        raise


def delete_one(collection_name, query):
    """Delete a single document"""
    try:
        collection = get_collection(collection_name)
        result = collection.delete_one(query)
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise


def delete_many(collection_name, query):
    """Delete multiple documents"""
    try:
        collection = get_collection(collection_name)
        result = collection.delete_many(query)
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting documents: {e}")
        raise


def count_documents(collection_name, query):
    """Count documents matching query"""
    try:
        collection = get_collection(collection_name)
        return collection.count_documents(query)
    except Exception as e:
        logger.error(f"Error counting documents: {e}")
        raise


def aggregate(collection_name, pipeline):
    """Run aggregation pipeline"""
    try:
        collection = get_collection(collection_name)
        result = list(collection.aggregate(pipeline))
        for doc in result:
            if '_id' in doc and isinstance(doc['_id'], ObjectId):
                doc['_id'] = str(doc['_id'])
        return result
    except Exception as e:
        logger.error(f"Error in aggregation: {e}")
        raise


# ============================================
# Helper Functions
# ============================================

def to_object_id(id_string):
    """Convert string to ObjectId"""
    try:
        return ObjectId(id_string)
    except Exception:
        return None


def is_valid_object_id(id_string):
    """Check if string is valid ObjectId"""
    try:
        ObjectId(id_string)
        return True
    except Exception:
        return False


def create_indexes(collection_name, indexes):
    """
    Create indexes on collection
    
    Args:
        collection_name (str): Collection name
        indexes (list): List of tuples (field, direction)
    """
    try:
        collection = get_collection(collection_name)
        collection.create_index(indexes)
        logger.info(f"Created indexes on {collection_name}: {indexes}")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


# ============================================
# Initialize Collections & Indexes
# ============================================

def initialize_mongodb_collections():
    """Create indexes for all collections"""
    try:
        # Domains
        create_indexes(COLLECTIONS['DOMAINS'], [('name', 1)])
        
        # Niches
        create_indexes(COLLECTIONS['NICHES'], [
            ('domain_id', 1),
            ('name', 1)
        ])
        
        # Audiences
        create_indexes(COLLECTIONS['AUDIENCES'], [
            ('domain_id', 1),
            ('name', 1)
        ])
        
        # Books
        create_indexes(COLLECTIONS['BOOKS'], [
            ('user_id', 1),
            ('status', 1),
            ('created_at', -1)
        ])
        
        # User Analytics
        create_indexes(COLLECTIONS['USER_ANALYTICS'], [
            ('user_id', 1),
            ('created_at', -1)
        ])
        
        logger.info("MongoDB collections initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing MongoDB collections: {e}")


# Call initialization when module is imported
if settings.MONGODB_DATABASE:
    try:
        initialize_mongodb_collections()
    except Exception as e:
        logger.warning(f"Could not initialize MongoDB collections: {e}")
