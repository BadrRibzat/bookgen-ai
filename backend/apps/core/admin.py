"""
Enhanced Django Admin configuration for Core app
Provides MongoDB data management through custom admin views
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from .services import DomainService, NicheService, AudienceService, DataSeedService
from .mongodb import get_collection, count_documents
import logging

logger = logging.getLogger(__name__)


class MongoDBAdminMixin:
    """Mixin for MongoDB-based admin functionality"""
    
    def get_mongodb_stats(self):
        """Get MongoDB collection statistics"""
        try:
            return {
                'domains': count_documents('domains', {}),
                'niches': count_documents('niches', {}),
                'audiences': count_documents('audiences', {}),
            }
        except Exception as e:
            logger.error(f"Error getting MongoDB stats: {e}")
            return {'domains': 0, 'niches': 0, 'audiences': 0}


class CoreDataManagementAdmin(admin.ModelAdmin, MongoDBAdminMixin):
    """Custom admin view for MongoDB data management"""
    
    change_list_template = 'admin/core_change_list.html'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
    
    def get_urls(self):
        """Add custom URLs for MongoDB management"""
        urls = super().get_urls()
        custom_urls = [
            path('mongodb-stats/', self.admin_site.admin_view(self.mongodb_stats_view), name='core_mongodb_stats'),
            path('seed-data/', self.admin_site.admin_view(self.seed_data_view), name='core_seed_data'),
            path('clear-data/', self.admin_site.admin_view(self.clear_data_view), name='core_clear_data'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Custom change list view with MongoDB stats"""
        extra_context = extra_context or {}
        extra_context['mongodb_stats'] = self.get_mongodb_stats()
        extra_context['title'] = 'BookGen-AI Core Data Management'
        return super().changelist_view(request, extra_context=extra_context)
    
    def mongodb_stats_view(self, request):
        """API endpoint for MongoDB statistics"""
        try:
            stats = self.get_mongodb_stats()
            
            # Get sample data
            domains = get_collection('domains').find().limit(5)
            niches = get_collection('niches').find().limit(5)
            audiences = get_collection('audiences').find().limit(5)
            
            data = {
                'stats': stats,
                'sample_domains': list(domains),
                'sample_niches': list(niches),
                'sample_audiences': list(audiences),
            }
            
            # Convert ObjectId to string for JSON serialization
            for collection in ['sample_domains', 'sample_niches', 'sample_audiences']:
                for item in data[collection]:
                    if '_id' in item:
                        item['_id'] = str(item['_id'])
            
            return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Error in MongoDB stats view: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def seed_data_view(self, request):
        """View for seeding initial data"""
        if request.method == 'POST':
            try:
                from .management.commands.seed_domains import Command
                command = Command()
                command.handle()
                
                messages.success(request, '✅ Data seeded successfully!')
                return JsonResponse({'success': True, 'message': 'Data seeded successfully'})
                
            except Exception as e:
                logger.error(f"Error seeding data: {e}")
                messages.error(request, f'❌ Error seeding data: {str(e)}')
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        # GET request - show confirmation page
        stats = self.get_mongodb_stats()
        return render(request, 'admin/seed_data_confirmation.html', {
            'title': 'Seed Initial Data',
            'current_stats': stats,
        })
    
    def clear_data_view(self, request):
        """View for clearing all data"""
        if request.method == 'POST':
            try:
                DataSeedService.clear_all_data()
                messages.success(request, '✅ All data cleared successfully!')
                return JsonResponse({'success': True, 'message': 'All data cleared successfully'})
                
            except Exception as e:
                logger.error(f"Error clearing data: {e}")
                messages.error(request, f'❌ Error clearing data: {str(e)}')
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        # GET request - show confirmation page
        stats = self.get_mongodb_stats()
        return render(request, 'admin/clear_data_confirmation.html', {
            'title': 'Clear All Data',
            'current_stats': stats,
            'warning_message': 'This will permanently delete all domains, niches, and audiences!'
        })


# Note: Since this is for MongoDB data management and we don't have actual Django models,
# we'll need to create the admin URLs through the main URL configuration instead
# of registering with admin.site.register()
