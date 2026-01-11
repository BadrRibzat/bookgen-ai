from celery import shared_task
from .services import BookService
from .models import BookGenerationRequest
from apps.core.mongodb import update_one, insert_one, COLLECTIONS
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task(name='apps.books.tasks.generate_book_task')
def generate_book_task(generation_request_id):
    """
    Background task to generate book content using LLM service.
    """
    logger.info(f"Starting book generation for request {generation_request_id}")

    try:
        # 1. Get the generation request
        generation_request = BookGenerationRequest.objects.get(id=generation_request_id)
        generation_request.status = 'processing'
        generation_request.started_at = timezone.now()
        generation_request.save()

        # 2. Generate content using LLM service
        prompt = f"Write a comprehensive book about '{generation_request.title}' in the {generation_request.domain.name} domain."
        if generation_request.custom_prompt:
            prompt += f" Additional requirements: {generation_request.custom_prompt}"

        llm_response = BookService.call_llm_service(
            prompt=prompt,
            domain_id=generation_request.domain.name,
            max_tokens=generation_request.target_word_count * 2  # Rough token estimate
        )

        if not llm_response or 'generated_text' not in llm_response:
            raise Exception("LLM generation failed or returned empty response")

        content = llm_response['generated_text'][0] if isinstance(llm_response['generated_text'], list) else llm_response['generated_text']

        # 3. Create book document in MongoDB
        book_doc = {
            'user_id': str(generation_request.user.id),
            'title': generation_request.title,
            'domain_id': generation_request.domain.name,
            'content': content,
            'word_count': len(content.split()),
            'status': 'completed',
            'created_at': datetime.utcnow(),
            'generation_request_id': str(generation_request.id)
        }

        book_result = insert_one(COLLECTIONS['BOOKS'], book_doc)
        mongodb_book_id = str(book_result.inserted_id)

        # 4. Create chapters (split content into chapters)
        chapters = BookService.split_content_into_chapters(content)

        for i, chapter in enumerate(chapters, 1):
            chapter_doc = {
                'book_id': mongodb_book_id,
                'title': chapter['title'],
                'content': chapter['content'],
                'order': i,
                'created_at': datetime.utcnow()
            }
            insert_one(COLLECTIONS['CHAPTERS'], chapter_doc)

        # 5. Generate PDF
        logger.info(f"Generating PDF for book {mongodb_book_id}")
        pdf_buffer = BookService.generate_pdf(book_doc, chapters)
        
        # Upload PDF to Cloudinary
        filename = f"book_{generation_request.id}_{generation_request.user.id}"
        pdf_url = BookService.upload_pdf_to_cloudinary(pdf_buffer, filename)
        
        if pdf_url:
            # Update book document with PDF URL
            update_one(
                COLLECTIONS['BOOKS'], 
                {'_id': book_result.inserted_id}, 
                {'pdf_url': pdf_url, 'updated_at': datetime.utcnow()}
            )
            logger.info(f"PDF uploaded successfully: {pdf_url}")
        else:
            logger.warning("PDF upload failed, continuing without PDF")

        # 6. Update generation request as completed
        generation_request.status = 'completed'
        generation_request.completed_at = timezone.now()
        generation_request.mongodb_book_id = mongodb_book_id
        generation_request.pdf_url = pdf_url or ''
        generation_request.tokens_used = llm_response.get('tokens_used', 0)
        generation_request.save()

        # 6. Update user stats
        stats = generation_request.user.generation_stats
        stats.books_generated_this_month += 1
        stats.total_books_generated += 1
        stats.last_generation_at = timezone.now()
        stats.save()

        logger.info(f"Book generation completed for request {generation_request_id}")
        return True

    except Exception as e:
        logger.error(f"Error in generate_book_task: {str(e)}")

        # Update request status to failed
        try:
            generation_request.status = 'failed'
            generation_request.error_message = str(e)
            generation_request.completed_at = timezone.now()
            generation_request.save()
        except Exception:
            pass  # Request might not exist

        return False
