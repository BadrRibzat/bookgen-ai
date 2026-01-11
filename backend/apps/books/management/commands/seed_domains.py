from django.core.management.base import BaseCommand
from apps.books.models import Domain

DOMAINS_DATA = [
    {
        'name': 'cybersecurity',
        'display_name': 'Cybersecurity',
        'description': 'Comprehensive guides on cybersecurity best practices, threat prevention, and digital protection strategies for individuals and organizations.',
        'icon': 'shield',
        'color': '#DC2626',
        'trending_score': 95,
    },
    {
        'name': 'ai_ml',
        'display_name': 'AI & Machine Learning',
        'description': 'In-depth explorations of artificial intelligence, machine learning algorithms, and their applications in modern technology.',
        'icon': 'brain',
        'color': '#7C3AED',
        'trending_score': 98,
    },
    {
        'name': 'nutrition',
        'display_name': 'Nutrition & Health',
        'description': 'Evidence-based nutrition guides, healthy eating plans, and wellness strategies for optimal physical and mental health.',
        'icon': 'heart',
        'color': '#059669',
        'trending_score': 85,
    },
    {
        'name': 'ecommerce',
        'display_name': 'E-commerce & Business',
        'description': 'Complete business guides covering online retail, digital marketing, customer acquisition, and scaling e-commerce operations.',
        'icon': 'shopping-cart',
        'color': '#EA580C',
        'trending_score': 90,
    },
    {
        'name': 'finance',
        'display_name': 'Personal Finance',
        'description': 'Comprehensive financial planning guides covering investing, budgeting, debt management, and wealth building strategies.',
        'icon': 'dollar-sign',
        'color': '#16A34A',
        'trending_score': 88,
    },
    {
        'name': 'productivity',
        'display_name': 'Productivity & Time Management',
        'description': 'Proven techniques for maximizing productivity, managing time effectively, and achieving professional and personal goals.',
        'icon': 'clock',
        'color': '#2563EB',
        'trending_score': 82,
    },
    {
        'name': 'marketing',
        'display_name': 'Digital Marketing',
        'description': 'Complete digital marketing strategies including SEO, social media marketing, content marketing, and conversion optimization.',
        'icon': 'megaphone',
        'color': '#DC2626',
        'trending_score': 87,
    },
    {
        'name': 'web_development',
        'display_name': 'Web Development',
        'description': 'Modern web development guides covering frontend technologies, backend systems, and full-stack development practices.',
        'icon': 'code',
        'color': '#7C3AED',
        'trending_score': 83,
    },
    {
        'name': 'data_science',
        'display_name': 'Data Science & Analytics',
        'description': 'Data-driven insights and analytical techniques for extracting value from data and making informed business decisions.',
        'icon': 'bar-chart',
        'color': '#0891B2',
        'trending_score': 86,
    },
    {
        'name': 'leadership',
        'display_name': 'Leadership & Management',
        'description': 'Essential leadership skills, team management strategies, and organizational development principles for effective leadership.',
        'icon': 'users',
        'color': '#92400E',
        'trending_score': 80,
    },
    {
        'name': 'blockchain',
        'display_name': 'Blockchain & Web3',
        'description': 'Comprehensive guides on blockchain technology, cryptocurrency, decentralized applications, and the future of Web3.',
        'icon': 'link',
        'color': '#4F46E5',
        'trending_score': 92,
    },
    {
        'name': 'sustainability',
        'display_name': 'Sustainability & Environment',
        'description': 'Practical guides for sustainable living, environmental conservation, and building eco-friendly businesses and lifestyles.',
        'icon': 'leaf',
        'color': '#16A34A',
        'trending_score': 78,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with initial domain data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding domains...')

        created_count = 0
        updated_count = 0

        for domain_data in DOMAINS_DATA:
            domain, created = Domain.objects.update_or_create(
                name=domain_data['name'],
                defaults=domain_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created domain: {domain.display_name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated domain: {domain.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} domains '
                f'({created_count} created, {updated_count} updated)'
            )
        )