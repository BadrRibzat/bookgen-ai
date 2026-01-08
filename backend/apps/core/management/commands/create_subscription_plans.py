"""
Management command to create subscription plans.
Usage: python manage.py create_subscription_plans
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create subscription plans for the SaaS platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating subscription plans...'))

        subscription_plans = [
            {
                'name': 'Personal (Wellness & Learning)',
                'slug': 'personal',
                'price': 19.00,
                'billing_cycle': 'monthly',
                'duration_days': 30,
                'book_limit_per_month': 10,
                'features': {
                    'domains': ['Nutrition & Meditation', 'Kids & Parenting', 'Recipes & Cooking'],
                    'pdf_quality': 'Standard',
                    'cover_templates': 'Basic',
                    'support': 'Email',
                    'max_pages': 15,
                    'commercial_use': False,
                },
                'is_active': True,
            },
            {
                'name': 'Creator (Social & Content)',
                'slug': 'creator',
                'price': 39.00,
                'billing_cycle': 'monthly',
                'duration_days': 30,
                'book_limit_per_month': 50,
                'features': {
                    'domains': ['Creator Economy', 'Kids & Parenting', 'Recipes', 'AI & ML'],
                    'pdf_quality': 'Premium',
                    'cover_customization': 'Advanced',
                    'social_media_formatting': True,
                    'support': 'Priority',
                    'max_pages': 30,
                    'commercial_use': True,
                },
                'is_active': True,
            },
            {
                'name': 'Professional (Education & Knowledge)',
                'slug': 'professional',
                'price': 79.00,
                'billing_cycle': 'monthly',
                'duration_days': 30,
                'book_limit_per_month': 200,
                'features': {
                    'domains': ['AI & ML', 'Automation', 'HealthTech', 'Data Analytics', 'Cybersecurity'],
                    'pdf_quality': 'Professional',
                    'branding': 'Custom',
                    'cover_designs': 'Custom',
                    'team_collaboration': 3,
                    'api_access': 'Limited',
                    'support': 'Phone',
                    'max_pages': 60,
                    'commercial_use': True,
                },
                'is_active': True,
            },
            {
                'name': 'Entrepreneur (Reselling)',
                'slug': 'entrepreneur',
                'price': 149.00,
                'billing_cycle': 'monthly',
                'duration_days': 30,
                'book_limit_per_month': -1,  # Unlimited
                'features': {
                    'domains': ['All 12 domains'],
                    'pdf_quality': 'White-label',
                    'commercial_rights': True,
                    'analytics': 'Advanced',
                    'api_access': 'Priority',
                    'account_manager': True,
                    'support': 'Dedicated',
                    'max_pages': -1,  # Unlimited
                    'commercial_use': True,
                },
                'is_active': True,
            },
            {
                'name': 'Enterprise (Custom Solutions)',
                'slug': 'enterprise',
                'price': 499.00,
                'billing_cycle': 'monthly',
                'duration_days': 30,
                'book_limit_per_month': -1,  # Unlimited
                'features': {
                    'domains': ['Custom domain sets + All standard'],
                    'ai_model_training': 'Custom',
                    'api_access': 'Full',
                    'security': 'SSO & Advanced',
                    'workflow_integration': 'Custom',
                    'support': '24/7 Premium',
                    'slas': True,
                    'max_pages': -1,  # Unlimited
                    'commercial_use': True,
                },
                'is_active': True,
            },
        ]

        with transaction.atomic():
            for plan_data in subscription_plans:
                slug = plan_data.pop('slug')

                # Check if plan already exists
                if SubscriptionPlan.objects.filter(slug=slug).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Plan {slug} already exists, skipping...')
                    )
                    continue

                # Create plan
                plan = SubscriptionPlan.objects.create(slug=slug, **plan_data)
        self.stdout.write(self.style.SUCCESS('\nSubscription plans created successfully!'))