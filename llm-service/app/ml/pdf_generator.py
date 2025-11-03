"""
PDF generation utilities using ReportLab
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from typing import Dict, List, Any
import logging
from datetime import datetime


class BookPDFGenerator:
    """Generate professional PDF books from generated content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for book formatting"""
        
        # Book title style
        self.styles.add(ParagraphStyle(
            name='BookTitle',
            parent=self.styles['Title'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E3A87'),  # Deep blue
            fontName='Helvetica-Bold'
        ))
        
        # Chapter title style
        self.styles.add(ParagraphStyle(
            name='ChapterTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceBefore=40,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#4A339A'),  # Purple from our logo
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BookBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=14
        ))
        
        # Author style
        self.styles.add(ParagraphStyle(
            name='Author',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#999999'),
            fontName='Helvetica'
        ))
    
    def generate_book_pdf(self, book_data: Dict[str, Any], output_path: str) -> bool:
        """
        Generate a complete book PDF
        
        Args:
            book_data: Dictionary containing book information
                {
                    'title': str,
                    'author': str,
                    'domain': str,
                    'niche': str,
                    'chapters': [
                        {
                            'title': str,
                            'content': str,
                            'sections': [
                                {
                                    'title': str,
                                    'content': str
                                }
                            ]
                        }
                    ],
                    'metadata': {
                        'generated_at': str,
                        'model_version': str,
                        'word_count': int
                    }
                }
            output_path: Path to save the PDF
        
        Returns:
            bool: Success status
        """
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=1*inch,
                leftMargin=1*inch,
                topMargin=1*inch,
                bottomMargin=1*inch
            )
            
            # Build the story (content elements)
            story = []
            
            # Title Page
            story.extend(self._create_title_page(book_data))
            
            # Table of Contents
            story.extend(self._create_table_of_contents(book_data))
            
            # Chapters
            for i, chapter in enumerate(book_data.get('chapters', []), 1):
                story.extend(self._create_chapter(chapter, i))
            
            # Footer information
            story.extend(self._create_footer(book_data))
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            self.logger.info(f"Book PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            return False
    
    def _create_title_page(self, book_data: Dict[str, Any]) -> List:
        """Create the title page"""
        elements = []
        
        # Add some space at top
        elements.append(Spacer(1, 2*inch))
        
        # Title
        title = book_data.get('title', 'Untitled Book')
        elements.append(Paragraph(title, self.styles['BookTitle']))
        
        # Subtitle (domain and niche)
        domain = book_data.get('domain', '')
        niche = book_data.get('niche', '')
        if domain and niche:
            subtitle = f"A Comprehensive Guide to {niche} in {domain}"
            elements.append(Paragraph(subtitle, self.styles['Author']))
        
        # Space
        elements.append(Spacer(1, 1*inch))
        
        # Author
        author = book_data.get('author', 'BookGen-AI')
        elements.append(Paragraph(f"by {author}", self.styles['Author']))
        
        # Generation info
        metadata = book_data.get('metadata', {})
        generated_at = metadata.get('generated_at', datetime.now().strftime('%Y-%m-%d'))
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(f"Generated on {generated_at}", self.styles['Footer']))
        elements.append(Paragraph("Powered by BookGen-AI", self.styles['Footer']))
        
        # Page break
        elements.append(PageBreak())
        
        return elements
    
    def _create_table_of_contents(self, book_data: Dict[str, Any]) -> List:
        """Create table of contents"""
        elements = []
        
        # TOC Title
        elements.append(Paragraph("Table of Contents", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 20))
        
        # Chapter entries
        chapters = book_data.get('chapters', [])
        for i, chapter in enumerate(chapters, 1):
            chapter_title = chapter.get('title', f'Chapter {i}')
            toc_entry = f"{i}. {chapter_title} ........................... {i + 2}"  # Approximate page numbers
            elements.append(Paragraph(toc_entry, self.styles['Normal']))
            elements.append(Spacer(1, 6))
        
        elements.append(PageBreak())
        
        return elements
    
    def _create_chapter(self, chapter_data: Dict[str, Any], chapter_num: int) -> List:
        """Create a chapter"""
        elements = []
        
        # Chapter title
        title = chapter_data.get('title', f'Chapter {chapter_num}')
        elements.append(Paragraph(f"Chapter {chapter_num}: {title}", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 20))
        
        # Chapter content
        content = chapter_data.get('content', '')
        if content:
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    elements.append(Paragraph(paragraph.strip(), self.styles['BookBody']))
                    elements.append(Spacer(1, 6))
        
        # Sections within chapter
        sections = chapter_data.get('sections', [])
        for section in sections:
            section_title = section.get('title', '')
            section_content = section.get('content', '')
            
            if section_title:
                elements.append(Paragraph(section_title, self.styles['SectionHeading']))
                elements.append(Spacer(1, 10))
            
            if section_content:
                paragraphs = section_content.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        elements.append(Paragraph(paragraph.strip(), self.styles['BookBody']))
                        elements.append(Spacer(1, 6))
        
        # Page break after chapter
        elements.append(PageBreak())
        
        return elements
    
    def _create_footer(self, book_data: Dict[str, Any]) -> List:
        """Create footer/back matter"""
        elements = []
        
        # About section
        elements.append(Paragraph("About This Book", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 20))
        
        metadata = book_data.get('metadata', {})
        about_text = f"""
        This book was generated using BookGen-AI, an advanced artificial intelligence system 
        specialized in creating domain-specific content. The content is based on extensive 
        training data from {book_data.get('domain', 'various')} domain sources and is 
        tailored for {book_data.get('niche', 'general')} applications.
        
        Generation Details:
        - Model Version: {metadata.get('model_version', 'v1.0')}
        - Generated: {metadata.get('generated_at', 'Unknown')}
        - Word Count: {metadata.get('word_count', 'Unknown')}
        - Domain: {book_data.get('domain', 'General')}
        - Niche: {book_data.get('niche', 'General')}
        """
        
        elements.append(Paragraph(about_text, self.styles['BookBody']))
        
        return elements
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page numbers to each page"""
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.setFillColor(colors.HexColor('#999999'))
        canvas_obj.drawCentredText(letter[0]/2, 0.5*inch, text)
    
    def generate_chapter_pdf(self, chapter_data: Dict[str, Any], output_path: str) -> bool:
        """Generate a single chapter as PDF"""
        
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=1*inch,
                leftMargin=1*inch,
                topMargin=1*inch,
                bottomMargin=1*inch
            )
            
            story = self._create_chapter(chapter_data, 1)
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            self.logger.info(f"Chapter PDF generated: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating chapter PDF: {e}")
            return False


class BookFormatter:
    """Format and structure generated content for book creation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_generated_content(self, raw_content: str, domain: str, niche: str) -> Dict[str, Any]:
        """Format raw generated content into structured book data"""
        
        # Basic formatting
        formatted_content = self._clean_and_format_text(raw_content)
        
        # Split into chapters (simple heuristic)
        chapters = self._split_into_chapters(formatted_content)
        
        # Create book structure
        book_data = {
            'title': self._generate_title(domain, niche, formatted_content),
            'author': 'BookGen-AI',
            'domain': domain,
            'niche': niche,
            'chapters': chapters,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'model_version': 'v1.0',
                'word_count': len(formatted_content.split()),
                'chapter_count': len(chapters)
            }
        }
        
        return book_data
    
    def _clean_and_format_text(self, text: str) -> str:
        """Clean and format raw text"""
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix sentence spacing
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        
        # Add paragraph breaks at appropriate points
        text = re.sub(r'\.([A-Z][^.]*?)\.', r'.\n\n\1.', text)
        
        return text
    
    def _split_into_chapters(self, content: str) -> List[Dict[str, Any]]:
        """Split content into chapters"""
        
        # Simple approach: split by length or natural breaks
        words = content.split()
        chapter_length = max(200, len(words) // 5)  # Aim for 5 chapters minimum
        
        chapters = []
        current_chapter = []
        
        for word in words:
            current_chapter.append(word)
            
            # Create chapter break
            if len(current_chapter) >= chapter_length and word.endswith('.'):
                chapter_content = ' '.join(current_chapter)
                chapter_title = self._generate_chapter_title(chapter_content, len(chapters) + 1)
                
                chapters.append({
                    'title': chapter_title,
                    'content': chapter_content,
                    'sections': []  # Could be expanded later
                })
                
                current_chapter = []
        
        # Add remaining content as final chapter
        if current_chapter:
            chapter_content = ' '.join(current_chapter)
            chapter_title = self._generate_chapter_title(chapter_content, len(chapters) + 1)
            
            chapters.append({
                'title': chapter_title,
                'content': chapter_content,
                'sections': []
            })
        
        return chapters
    
    def _generate_title(self, domain: str, niche: str, content: str) -> str:
        """Generate a book title"""
        
        # Extract key terms from content
        words = content.lower().split()[:100]  # First 100 words
        
        # Simple title generation
        if 'guide' in words or 'how' in words:
            return f"The Complete Guide to {niche} in {domain}"
        elif 'introduction' in words or 'basic' in words:
            return f"Introduction to {niche}: A {domain} Perspective"
        else:
            return f"Mastering {niche}: Advanced {domain} Strategies"
    
    def _generate_chapter_title(self, content: str, chapter_num: int) -> str:
        """Generate a chapter title from content"""
        
        # Extract first meaningful sentence or phrase
        sentences = content.split('.')[:3]
        first_sentence = sentences[0].strip() if sentences else f"Chapter {chapter_num}"
        
        # Clean up the title
        words = first_sentence.split()[:8]  # Limit to 8 words
        title = ' '.join(words)
        
        # Remove common starting words
        for start_word in ['the', 'this', 'in', 'on', 'for', 'with']:
            if title.lower().startswith(start_word + ' '):
                title = title[len(start_word):].strip()
                break
        
        return title.title() if title else f"Chapter {chapter_num}"