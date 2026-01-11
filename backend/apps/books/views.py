from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
import logging

from .models import Domain, BookGenerationRequest, UserGenerationStats
from .serializers import (
    DomainSerializer, BookGenerationRequestListSerializer,
    BookGenerationRequestDetailSerializer, BookGenerationRequestCreateSerializer,
    UserGenerationStatsSerializer
)
from .services import BookService
from .tasks import generate_book_task

logger = logging.getLogger(__name__)


class DomainListView(ListAPIView):
    """
    List available domains for book generation.
    GET /api/books/domains/
    """
    queryset = Domain.objects.filter(is_active=True)
    serializer_class = DomainSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookGenerationStatsView(APIView):
    """
    User's book generation statistics and limits.
    GET /api/books/stats/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: UserGenerationStatsSerializer})
    def get(self, request):
        """Get user's generation statistics"""
        stats, created = UserGenerationStats.objects.get_or_create(user=request.user)
        serializer = UserGenerationStatsSerializer(stats)
        return Response(serializer.data)


class BookGenerationRequestListView(ListAPIView):
    """
    List user's book generation requests.
    GET /api/books/generation-requests/
    """
    serializer_class = BookGenerationRequestListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookGenerationRequest.objects.filter(user=self.request.user)


class BookGenerationRequestDetailView(RetrieveAPIView):
    """
    Get details of a specific book generation request.
    GET /api/books/generation-requests/<id>/
    """
    serializer_class = BookGenerationRequestDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookGenerationRequest.objects.filter(user=self.request.user)


class BookGenerationCreateView(APIView):
    """
    Create a new book generation request.
    POST /api/books/generate/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=BookGenerationRequestCreateSerializer,
        responses={201: BookGenerationRequestDetailSerializer}
    )
    def post(self, request):
        """Create and start book generation"""
        serializer = BookGenerationRequestCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            # Create the generation request
            generation_request = serializer.save(user=request.user)

            # Get or create user stats
            stats, created = UserGenerationStats.objects.get_or_create(user=request.user)

            # Check limits
            if not stats.can_generate_book():
                generation_request.delete()
                return Response({
                    'error': 'Monthly generation limit reached'
                }, status=status.HTTP_403_FORBIDDEN)

            # Increment usage
            stats.increment_generation_count()

            # Start the generation task
            generate_book_task.delay(str(generation_request.id))

            # Return the created request
            response_serializer = BookGenerationRequestDetailSerializer(generation_request)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookPreviewView(APIView):
    """
    Preview a generated book.
    GET /api/books/<generation_request_id>/preview/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, generation_request_id):
        """Get book preview from MongoDB"""
        generation_request = get_object_or_404(
            BookGenerationRequest,
            id=generation_request_id,
            user=request.user
        )

        if not generation_request.mongodb_book_id:
            return Response({
                'error': 'Book not yet generated'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get book content from MongoDB
        book_data = BookService.get_book_details(generation_request.mongodb_book_id)
        if not book_data:
            return Response({
                'error': 'Book content not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Mark as previewed
        generation_request.is_previewed = True
        generation_request.save()

        return Response({
            'generation_request': BookGenerationRequestDetailSerializer(generation_request).data,
            'book_content': book_data
        })


class BookDownloadView(APIView):
    """
    Download a generated book as PDF.
    GET /api/books/<generation_request_id>/download/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, generation_request_id):
        """Download book PDF"""
        generation_request = get_object_or_404(
            BookGenerationRequest,
            id=generation_request_id,
            user=request.user,
            status='completed'
        )

        if not generation_request.can_download:
            return Response({
                'error': 'Download not allowed for your subscription'
            }, status=status.HTTP_403_FORBIDDEN)

        if not generation_request.pdf_file:
            return Response({
                'error': 'PDF not yet generated'
            }, status=status.HTTP_404_NOT_FOUND)

        # Mark as downloaded
        generation_request.is_downloaded = True
        generation_request.downloaded_at = timezone.now()
        generation_request.save()

        # Return file URL or serve file
        return Response({
            'download_url': request.build_absolute_uri(generation_request.pdf_file.url),
            'filename': f"{generation_request.title}.pdf"
        })


class BookDeleteView(APIView):
    """
    Delete a book generation request and associated files.
    DELETE /api/books/<generation_request_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, generation_request_id):
        """Delete book and clean up files"""
        generation_request = get_object_or_404(
            BookGenerationRequest,
            id=generation_request_id,
            user=request.user
        )

        # Delete associated files
        if generation_request.pdf_file:
            generation_request.pdf_file.delete()
        if generation_request.cover_image:
            generation_request.cover_image.delete()

        # Delete MongoDB content if exists
        if generation_request.mongodb_book_id:
            BookService.delete_book(generation_request.mongodb_book_id, str(request.user.id))

        # Delete the request
        generation_request.delete()

        return Response({
            'message': 'Book deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
