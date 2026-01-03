from celery import shared_task
from .services import BookService
from apps.core.mongodb import update_one, insert_one, COLLECTIONS, to_object_id
from apps.users.models import User
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task(name='apps.books.tasks.generate_book_task')
def generate_book_task(book_id, user_id):
    """
    Background task to generate book content using LLM service.
    """
    logger.info(f"Starting book generation for book {book_id} (User: {user_id})")
    
    try:
        # 1. Fetch book details
        book = BookService.get_book_details(book_id)
        if not book:
            logger.error(f"Book {book_id} not found in MongoDB")
            return False
            
        # 2. Update status to 'processing'
        update_one(COLLECTIONS['BOOKS'], {'_id': book_id}, {'$set': {'status': 'processing'}})
        
        # 3. Generate content (MVP: Generate one main chapter/content)
        prompt = f"Write a comprehensive guide about {book['title']} in the {book['domain_id']} domain."
        if book.get('niche_id'):
            prompt += f" Focus on the {book['niche_id']} niche."
            
        llm_response = BookService.call_llm_service(
            prompt=prompt,
            domain_id=book['domain_id'],
            niche_id=book.get('niche_id')
        )
        
        if not llm_response or 'generated_text' not in llm_response:
            raise Exception("LLM generation failed or returned empty response")
            
        content = llm_response['generated_text'][0]
        
        # 4. Create a chapter for the book
        chapter_doc = {
            'book_id': str(book_id),
            'title': 'Main Content',
            'content': content,
            'order': 1,
            'created_at': datetime.utcnow()
        }
        insert_one(COLLECTIONS['CHAPTERS'], chapter_doc)
        
        # 5. Update book status to 'completed' and add summary
        summary = content[:500] + "..." if len(content) > 500 else content
        update_one(COLLECTIONS['BOOKS'], {'_id': book_id}, {
            '$set': {
                'status': 'completed',
                'summary': summary,
                'completed_at': datetime.utcnow()
            }
        })
        
        # 6. Update User analytics
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            profile.total_books_generated += 1
            profile.total_words_written += len(content.split())
            profile.last_active_at = timezone.now() # Need to import timezone
            profile.save()
        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found when updating analytics")
            
        logger.info(f"Book generation completed for book {book_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error in generate_book_task: {str(e)}")
        update_one(COLLECTIONS['BOOKS'], {'_id': book_id}, {
            '$set': {
                'status': 'failed',
                'error': str(e)
            }
        })
        return False
