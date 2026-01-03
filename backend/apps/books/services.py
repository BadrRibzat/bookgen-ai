"""
Services for managing Books in MongoDB.
"""

from apps.core.mongodb import (
    find_one,
    find_many,
    insert_one,
    update_one,
    delete_one,
    delete_many,
    COLLECTIONS,
    to_object_id
)
from datetime import datetime
import requests
from django.conf import settings

class BookService:
    """Service class for Book operations"""

    @staticmethod
    def get_user_books(user_id, limit=20, skip=0):
        """Get books for a specific user"""
        query = {'user_id': user_id}
        books = find_many(COLLECTIONS['BOOKS'], query, limit=limit, skip=skip, sort=[('created_at', -1)])
        return books

    @staticmethod
    def get_book_details(book_id, user_id=None):
        """Get book details including chapters"""
        query = {'_id': book_id}
        if user_id:
            query['user_id'] = user_id
            
        book = find_one(COLLECTIONS['BOOKS'], query)
        if book:
            # Fetch chapters
            chapters_query = {'book_id': book_id}
            chapters = find_many('chapters', chapters_query, sort=[('order', 1)]) # Need to add chapters to COLLECTIONS
            book['chapters'] = chapters
        return book

    @staticmethod
    def create_book(user_id, title, domain_id, niche_id=None, metadata=None):
        """Create a new book entry"""
        book_doc = {
            'user_id': user_id,
            'title': title,
            'domain_id': domain_id,
            'niche_id': niche_id,
            'status': 'pending',
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return insert_one(COLLECTIONS['BOOKS'], book_doc)

    @staticmethod
    def call_llm_service(prompt, domain_id, niche_id=None):
        """Call the LLM service for text generation"""
        url = f"{settings.LLM_SERVICE_URL}/generate"
        payload = {
            'prompt': prompt,
            'domain_id': domain_id,
            'niche_id': niche_id,
            'max_length': 512,
            'repetition_penalty': 1.1,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            from logging import getLogger
            logger = getLogger(__name__)
            logger.error(f"LLM Service call failed: {str(e)}")
            return None

    @staticmethod
    def delete_book(book_id, user_id):
        """Delete a book and its chapters"""
        query = {'_id': to_object_id(book_id), 'user_id': user_id}
        deleted_count = delete_one(COLLECTIONS['BOOKS'], query)
        if deleted_count:
            # Delete chapters too
            chapters_query = {'book_id': str(book_id)}
            delete_many(COLLECTIONS['CHAPTERS'], chapters_query)
        return deleted_count
