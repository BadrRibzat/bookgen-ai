from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import BookService
from .tasks import generate_book_task
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
import logging

logger = logging.getLogger(__name__)

class BookHistoryView(APIView):
    """
    User's book generation history.
    GET /api/books/history/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("per_page", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        """Get authenticated user's book history from MongoDB."""
        try:
            user_id = request.user.id
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 20))
            skip = (page - 1) * per_page
            
            books = BookService.get_user_books(user_id, limit=per_page, skip=skip)
            
            return Response({
                'success': True,
                'books': books,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(books), # This should be a count query for accuracy
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching book history: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'code': 'FETCH_ERROR',
                    'message': 'Failed to retrieve book history.'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookDetailView(APIView):
    """
    View, update or delete a specific book.
    GET/DELETE /api/books/<id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, book_id):
        """Get specific book details including chapters."""
        book = BookService.get_book_details(book_id, user_id=request.user.id)
        if not book:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Book not found.'
                }
            }, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            'success': True,
            'book': book
        }, status=status.HTTP_200_OK)

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def delete(self, request, book_id):
        """Delete a book."""
        deleted_count = BookService.delete_book(book_id, request.user.id)
        if not deleted_count:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Book not found or already deleted.'
                }
            }, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            'success': True,
            'message': 'Book deleted successfully.'
        }, status=status.HTTP_200_OK)


class BookGenerateView(APIView):
    """
    Trigger book generation.
    POST /api/books/generate/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses={202: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        """Start the background generation process."""
        user = request.user
        profile = user.profile
        plan = profile.subscription_plan
        
        # Check usage limits
        limit = plan.book_limit_per_month if plan else 0
        if profile.current_month_book_count >= limit:
            return Response({
                'success': False,
                'error': {
                    'code': 'LIMIT_REACHED',
                    'message': f'You have reached your monthly limit of {limit} books. Please upgrade your plan.'
                }
            }, status=status.HTTP_403_FORBIDDEN)
            
        # Extract generation params
        title = request.data.get('title')
        domain_id = request.data.get('domain_id')
        niche_id = request.data.get('niche_id')
        
        if not all([title, domain_id]):
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': 'Title and domain_id are required.'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Create book entry (status: pending)
        book_id = BookService.create_book(user.id, title, domain_id, niche_id)
        
        # Trigger Celery task
        generate_book_task.delay(str(book_id), user.id)
        
        # Increment usage count
        profile.current_month_book_count += 1
        profile.save()
        
        return Response({
            'success': True,
            'message': 'Book generation started.',
            'book_id': book_id
        }, status=status.HTTP_202_ACCEPTED)
