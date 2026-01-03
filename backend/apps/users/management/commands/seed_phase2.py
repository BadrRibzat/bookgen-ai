from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User, SubscriptionPlan, UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Seed initial subscription plans and the admin account for Phase 2'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Phase 2 data...')
        
        with transaction.atomic():
            # 1. Create Subscription Plans
            plans_data = [
                {
                    'name': 'Free',
                    'slug': 'free',
                    'price': 0.00,
                    'book_limit_per_month': 3,
                    'features': {
                        'high_quality': False,
                        'downloads': False,
                        'priority_support': False
                    }
                },
                {
                    'name': 'Pro',
                    'slug': 'pro',
                    'price': 29.00,
                    'book_limit_per_month': 20,
                    'features': {
                        'high_quality': True,
                        'downloads': True,
                        'priority_support': False
                    }
                },
                {
                    'name': 'Enterprise',
                    'slug': 'enterprise',
                    'price': 99.00,
                    'book_limit_per_month': 100,
                    'features': {
                        'high_quality': True,
                        'downloads': True,
                        'priority_support': True
                    }
                }
            ]
            
            plans = {}
            for data in plans_data:
                plan, created = SubscriptionPlan.objects.update_or_create(
                    slug=data['slug'],
                    defaults=data
                )
                plans[data['slug']] = plan
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created plan: {plan.name}'))
                else:
                    self.stdout.write(f'Updated plan: {plan.name}')

            # 2. Create Admin Superuser
            admin_email = 'badrribzat@gmail.com'
            admin_password = '@Badr1990'
            
            admin_user, created = User.objects.get_or_create(
                email=admin_email,
                defaults={
                    'first_name': 'Badr',
                    'last_name': 'Admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                    'email_verified': True,
                }
            )
            
            if created:
                admin_user.set_password(admin_password)
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email}'))
            else:
                self.stdout.write(f'Admin user already exists: {admin_email}')

            # 3. Ensure Admin has Enterprise plan
            profile = admin_user.profile
            profile.subscription_plan = plans['enterprise']
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Assigned Enterprise plan to admin: {admin_email}'))

        self.stdout.write(self.style.SUCCESS('Phase 2 seeding completed successfully!'))
