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
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
import cloudinary.uploader
from io import BytesIO
import logging

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
    def call_llm_service(prompt, domain_id, niche_id=None, max_length=512):
        """Call the LLM service for text generation"""
        url = f"{settings.LLM_SERVICE_URL}/generate"
        payload = {
            'prompt': prompt,
            'domain_id': domain_id,
            'niche_id': niche_id,
            'max_length': max_length,
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
    def split_content_into_chapters(content):
        """Split generated content into logical chapters"""
        # Simple chapter splitting based on content structure
        # This is a basic implementation - could be enhanced with ML

        paragraphs = content.split('\n\n')
        chapters = []
        current_chapter = {'title': 'Introduction', 'content': ''}

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if this looks like a chapter title
            if len(para.split()) < 10 and (para.isupper() or para.istitle()):
                # Save previous chapter
                if current_chapter['content'].strip():
                    chapters.append(current_chapter)

                # Start new chapter
                current_chapter = {
                    'title': para,
                    'content': ''
                }
            else:
                # Add to current chapter
                if current_chapter['content']:
                    current_chapter['content'] += '\n\n'
                current_chapter['content'] += para

        # Add the last chapter
        if current_chapter['content'].strip():
            chapters.append(current_chapter)

        # If no chapters were identified, create a single chapter
        if not chapters:
            chapters = [{
                'title': 'Main Content',
                'content': content
            }]

        return chapters

    @staticmethod
    def generate_pdf(book_data, chapters):
        """Generate PDF from book data and chapters"""
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        chapter_title_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkgreen
        )
        
        content_style = styles['Normal']
        content_style.fontSize = 12
        content_style.leading = 16
        
        story = []
        
        # Title page
        story.append(Paragraph(book_data.get('title', 'Generated Book'), title_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Add metadata if available
        if book_data.get('metadata'):
            metadata = book_data['metadata']
            if metadata.get('author'):
                story.append(Paragraph(f"Author: {metadata['author']}", styles['Normal']))
            if metadata.get('description'):
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph(metadata['description'], styles['Italic']))
        
        story.append(PageBreak())
        
        # Table of contents
        story.append(Paragraph("Table of Contents", styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        for i, chapter in enumerate(chapters, 1):
            toc_entry = f"{i}. {chapter.get('title', f'Chapter {i}')}"
            story.append(Paragraph(toc_entry, styles['Normal']))
        
        story.append(PageBreak())
        
        # Chapters
        for i, chapter in enumerate(chapters, 1):
            # Chapter title
            chapter_title = f"Chapter {i}: {chapter.get('title', f'Chapter {i}')}"
            story.append(Paragraph(chapter_title, chapter_title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Chapter content
            content = chapter.get('content', '')
            if content:
                # Split content into paragraphs
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        story.append(Paragraph(para, content_style))
                        story.append(Spacer(1, 0.1*inch))
            
            # Page break between chapters (except for the last one)
            if i < len(chapters):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def upload_pdf_to_cloudinary(pdf_buffer, filename):
        """Upload PDF to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                pdf_buffer,
                resource_type="raw",
                public_id=filename,
                folder="bookgen-ai/books/",
                format="pdf"
            )
            return result.get('secure_url')
        except Exception as e:
            from logging import getLogger
            logger = getLogger(__name__)
            logger.error(f"Cloudinary upload failed: {str(e)}")
            return None

    @staticmethod
    def generate_book_cover(title, domain_name, niche_name=None, style="professional"):
        """Generate AI book cover image"""
        # This is a placeholder for AI image generation
        # In production, integrate with DALL-E, Midjourney, or Stable Diffusion
        
        prompt = f"Create a professional book cover for a book titled '{title}' about {domain_name}"
        if niche_name:
            prompt += f" in the {niche_name} niche"
        
        prompt += ". Style should be modern, clean, and professional with relevant imagery."
        
        # TODO: Integrate with AI image generation service
        # For now, return a placeholder URL or generate a simple cover
        
        # Placeholder: In a real implementation, you would:
        # 1. Call an AI image generation API (DALL-E, Midjourney, etc.)
        # 2. Upload the generated image to Cloudinary
        # 3. Return the Cloudinary URL
        
        logger = logging.getLogger(__name__)
        logger.info(f"Cover generation requested for: {title} - {prompt}")
        
        # Return None for now - cover generation will be implemented later
        return None

    @staticmethod
    def upload_cover_to_cloudinary(image_buffer, filename):
        """Upload cover image to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                image_buffer,
                public_id=filename,
                folder="bookgen-ai/covers/",
                format="png"
            )
            return result.get('secure_url')
        except Exception as e:
            from logging import getLogger
            logger = getLogger(__name__)
            logger.error(f"Cover upload failed: {str(e)}")
            return None
