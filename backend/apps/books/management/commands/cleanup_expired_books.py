from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.books.models import BookGenerationRequest
from apps.books.services import BookService
from apps.core.mongodb import delete_one, delete_many, COLLECTIONS
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up expired book generation requests and associated files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after completion to consider books expired (default: 30)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']

        # Find expired book generation requests
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        expired_requests = BookGenerationRequest.objects.filter(
            auto_delete_after__lte=timezone.now(),
            status='completed'
        )

        self.stdout.write(
            self.style.SUCCESS(f"Found {expired_requests.count()} expired book requests")
        )

        deleted_count = 0
        for request in expired_requests:
            try:
                if dry_run:
                    self.stdout.write(
                        f"Would delete: {request.title} (ID: {request.id})"
                    )
                else:
                    # Delete from MongoDB
                    if request.mongodb_book_id:
                        # Delete book document
                        delete_one(COLLECTIONS['BOOKS'], {'_id': request.mongodb_book_id})

                        # Delete associated chapters
                        delete_many(COLLECTIONS['CHAPTERS'], {'book_id': request.mongodb_book_id})

                        self.stdout.write(
                            f"Deleted MongoDB data for book: {request.title}"
                        )

                    # Delete files from Cloudinary (if they exist)
                    # Note: Cloudinary files are not automatically deleted here
                    # They can be cleaned up via Cloudinary's lifecycle management

                    # Delete the request record
                    request.delete()

                    deleted_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Deleted: {request.title}")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error deleting {request.title}: {str(e)}")
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"Dry run completed. Would have deleted {expired_requests.count()} books.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {deleted_count} expired books.")
            )