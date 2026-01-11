import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.books.models import Domain, BookGenerationRequest, UserGenerationStats
from apps.books.services import BookService
from apps.books.serializers import DomainSerializer, BookGenerationRequestDetailSerializer
from unittest.mock import patch, MagicMock
from io import BytesIO


User = get_user_model()


class DomainModelTest(TestCase):
    def setUp(self):
        self.domain = Domain.objects.create(
            name='test_domain',
            display_name='Test Domain',
            description='A test domain for books',
            icon='book',
            color='#FF0000',
            trending_score=50
        )

    def test_domain_creation(self):
        self.assertEqual(self.domain.name, 'test_domain')
        self.assertEqual(self.domain.display_name, 'Test Domain')
        self.assertEqual(self.domain.trending_score, 50)
        self.assertTrue(self.domain.is_active)

    def test_domain_str(self):
        self.assertEqual(str(self.domain), 'Test Domain')


class BookGenerationRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.domain = Domain.objects.create(
            name='test_domain',
            display_name='Test Domain',
            description='A test domain'
        )
        self.request = BookGenerationRequest.objects.create(
            user=self.user,
            domain=self.domain,
            title='Test Book',
            target_word_count=10000
        )

    def test_request_creation(self):
        self.assertEqual(self.request.title, 'Test Book')
        self.assertEqual(self.request.status, 'pending')
        self.assertEqual(self.request.target_word_count, 10000)

    def test_can_download_property(self):
        # Without subscription, should return False
        self.assertFalse(self.request.can_download)

        # Mark as completed
        self.request.status = 'completed'
        self.request.save()
        self.assertFalse(self.request.can_download)  # Still false without subscription


class UserGenerationStatsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.stats = UserGenerationStats.objects.create(user=self.user)

    def test_stats_creation(self):
        self.assertEqual(self.stats.books_generated_this_month, 0)
        self.assertEqual(self.stats.total_books_generated, 0)

    def test_increment_generation_count(self):
        self.stats.increment_generation_count()
        self.assertEqual(self.stats.books_generated_this_month, 1)
        self.assertEqual(self.stats.total_books_generated, 1)
        self.assertIsNotNone(self.stats.last_generation_at)


class BookServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    @patch('apps.books.services.requests.post')
    def test_call_llm_service_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'generated_text': 'Test content'}
        mock_post.return_value = mock_response

        result = BookService.call_llm_service('test prompt', 'test_domain')
        self.assertEqual(result, {'generated_text': 'Test content'})

    @patch('apps.books.services.requests.post')
    def test_call_llm_service_failure(self, mock_post):
        mock_post.side_effect = Exception('API Error')

        result = BookService.call_llm_service('test prompt', 'test_domain')
        self.assertIsNone(result)

    def test_split_content_into_chapters(self):
        content = """Introduction

This is the introduction.

Chapter 1: Getting Started

This is chapter 1 content.

Chapter 2: Advanced Topics

This is chapter 2 content."""

        chapters = BookService.split_content_into_chapters(content)

        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0]['title'], 'Introduction')
        self.assertEqual(chapters[1]['title'], 'Chapter 1: Getting Started')

    @patch('apps.books.services.cloudinary.uploader.upload')
    def test_upload_pdf_to_cloudinary_success(self, mock_upload):
        mock_upload.return_value = {'secure_url': 'https://example.com/test.pdf'}

        pdf_buffer = BytesIO(b'test pdf content')
        result = BookService.upload_pdf_to_cloudinary(pdf_buffer, 'test_filename')

        self.assertEqual(result, 'https://example.com/test.pdf')
        mock_upload.assert_called_once()

    @patch('apps.books.services.cloudinary.uploader.upload')
    def test_upload_pdf_to_cloudinary_failure(self, mock_upload):
        mock_upload.side_effect = Exception('Upload failed')

        pdf_buffer = BytesIO(b'test pdf content')
        result = BookService.upload_pdf_to_cloudinary(pdf_buffer, 'test_filename')

        self.assertIsNone(result)


class SerializerTest(TestCase):
    def setUp(self):
        self.domain = Domain.objects.create(
            name='test_domain',
            display_name='Test Domain',
            description='A test domain'
        )

    def test_domain_serializer(self):
        serializer = DomainSerializer(self.domain)
        data = serializer.data

        self.assertEqual(data['name'], 'test_domain')
        self.assertEqual(data['display_name'], 'Test Domain')
        self.assertEqual(data['description'], 'A test domain')

    def test_book_generation_request_detail_serializer(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        request = BookGenerationRequest.objects.create(
            user=user,
            domain=self.domain,
            title='Test Book'
        )

        serializer = BookGenerationRequestDetailSerializer(request)
        data = serializer.data

        self.assertEqual(data['title'], 'Test Book')
        self.assertEqual(data['status'], 'pending')
        self.assertIn('domain', data)
        self.assertIn('pdf_url', data)
        self.assertIn('cover_url', data)