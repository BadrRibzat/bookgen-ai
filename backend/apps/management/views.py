from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.models import User, UserProfile, SubscriptionPlan
from apps.users.serializers import UserSerializer, SubscriptionPlanSerializer
from apps.books.services import BookService
from apps.core.mongodb import find_many, COLLECTIONS, count_documents
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
import logging

logger = logging.getLogger(__name__)

class AdminUserListView(generics.ListCreateAPIView):
    """
    Admin user management.
    GET/POST /api/management-secure/users/
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin user detail/update/delete.
    GET/PATCH/DELETE /api/management-secure/users/<id>/
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AdminBookListView(APIView):
    """
    Admin book management (all users).
    GET /api/management-secure/books/
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        responses={200: OpenApiTypes.OBJECT},
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("per_page", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ]
    )
    def get(self, request):
        """List all books from all users."""
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 50))
        skip = (page - 1) * per_page
        
        books = find_many(COLLECTIONS['BOOKS'], {}, limit=per_page, skip=skip, sort=[('created_at', -1)])
        total = count_documents(COLLECTIONS['BOOKS'], {})
        
        # Map _id to id for frontend compatibility
        for book in books:
            if '_id' in book:
                book['id'] = book.pop('_id')
        
        return Response({
            'success': True,
            'books': books,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
            }
        })

class AdminStatsView(APIView):
    """
    Admin analytics and income reporting.
    GET /api/management-secure/analytics/
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        """Get system-wide stats."""
        total_users = User.objects.count()
        total_books = count_documents(COLLECTIONS['BOOKS'], {})
        
        # Simple income calculation based on subscription prices
        # In a real app, this would query a Payments/Incomes model
        pro_plan = SubscriptionPlan.objects.filter(slug='pro').first()
        ent_plan = SubscriptionPlan.objects.filter(slug='enterprise').first()
        
        pro_count = UserProfile.objects.filter(subscription_plan=pro_plan).count()
        ent_count = UserProfile.objects.filter(subscription_plan=ent_plan).count()
        
        estimated_monthly_income = (pro_count * (pro_plan.price if pro_plan else 0)) + \
                                   (ent_count * (ent_plan.price if ent_plan else 0))
        
        return Response({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_books': total_books,
                'subscribers': {
                    'pro': pro_count,
                    'enterprise': ent_count,
                },
                'estimated_monthly_income': estimated_monthly_income,
            }
        })
