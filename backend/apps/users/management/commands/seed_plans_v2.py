from django.core.management.base import BaseCommand
from apps.users.models import SubscriptionPlan
from django.db import transaction

class Command(BaseCommand):
    help = 'Seed updated subscription plans (Phase 3)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Phase 3 Subscription Plans...')
        
        plans_data = [
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
                    'description': 'Perfect for individuals and hobbyists.'
                }
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
                    'social_formatting': True,
                    'support': 'Priority',
                    'description': 'Ideal for social media creators and influencers.'
                }
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
                    'pdf_branding': True,
                    'custom_covers': True,
                    'team_seats': 3,
                    'api_access': 'Limited',
                    'support': 'Phone',
                    'description': 'The power-house for professionals and small teams.'
                }
            },
            {
                'name': 'Entrepreneur (Reselling)',
                'slug': 'entrepreneur',
                'price': 149.00,
                'billing_cycle': 'monthly',
                'duration_days': 30,
                'book_limit_per_month': 9999,  # Effectively unlimited for PoC
                'features': {
                    'domains': ['All 12 domains'],
                    'white_label': True,
                    'commercial_rights': True,
                    'advanced_analytics': True,
                    'api_access': 'Priority',
                    'support': 'Dedicated Account Manager',
                    'description': 'Built for scale and commercial reselling.'
                }
            },
            {
                'name': 'Enterprise (Custom Solutions)',
                'slug': 'enterprise',
                'price': 499.00,
                'billing_cycle': 'monthly',
                'duration_days': 30,
                'book_limit_per_month': 99999,
                'features': {
                    'domains': ['Custom domain sets + All standard'],
                    'custom_ai_training': True,
                    'full_api': True,
                    'sso': True,
                    'custom_workflow': True,
                    'support': '24/7 Premium',
                    'sla': True,
                    'description': 'Custom-tailored solutions for large organizations.'
                }
            }
        ]
        
        with transaction.atomic():
            for data in plans_data:
                plan, created = SubscriptionPlan.objects.update_or_create(
                    slug=data['slug'],
                    defaults=data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created plan: {plan.name}'))
                else:
                    self.stdout.write(f'Updated plan: {plan.name}')

        self.stdout.write(self.style.SUCCESS('Subscription plans seeding completed!'))
