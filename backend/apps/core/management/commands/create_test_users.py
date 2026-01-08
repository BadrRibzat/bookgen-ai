"""
Management command to create test user accounts.
Usage: python manage.py create_test_users
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import User, SubscriptionPlan


class Command(BaseCommand):
    help = 'Create test user accounts for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test user accounts...'))
        
        # Get or create Personal plan for test users
        try:
            personal_plan = SubscriptionPlan.objects.get(slug='personal')
        except SubscriptionPlan.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Personal subscription plan not found. Creating it...')
            )
            personal_plan = SubscriptionPlan.objects.create(
                name='Personal (Wellness & Learning)',
                slug='personal',
                price=19.00,
                billing_cycle='monthly',
                duration_days=30,
                book_limit_per_month=10,
                features={'domains': ['Nutrition & Meditation', 'Kids & Parenting', 'Recipes & Cooking']},
                is_active=True,
            )
        
        test_users = [
            {
                'email': 'admin@bookgen.ai',
                'password': 'Admin@12345',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'email_verified': True,
                'subscription_plan': None,  # Admin gets no plan (unlimited)
            },
            {
                'email': 'user@example.com',
                'password': 'User@12345',
                'first_name': 'Test',
                'last_name': 'User',
                'email_verified': True,
                'subscription_plan': personal_plan,
            },
            {
                'email': 'newuser@example.com',
                'password': 'User@12345',
                'first_name': 'New',
                'last_name': 'User',
                'email_verified': False,
                'subscription_plan': personal_plan,
            },
        ]
        
        with transaction.atomic():
            for user_data in test_users:
                email = user_data.pop('email')
                password = user_data.pop('password')
                subscription_plan = user_data.pop('subscription_plan', None)
                
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User {email} already exists, skipping...')
                    )
                    continue
                
                # Create user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    **user_data
                )
                
                # Assign subscription plan if provided
                if subscription_plan:
                    user.profile.subscription_plan = subscription_plan
                    user.profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created user: {email} (Plan: {subscription_plan.name})')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created user: {email}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\nTest accounts created successfully!'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin: admin@bookgen.ai / Admin@12345')
        self.stdout.write('  User:  user@example.com / User@12345')
        self.stdout.write('  New:   newuser@example.com / User@12345')
