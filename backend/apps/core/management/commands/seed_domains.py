"""
Management command to seed domains, niches, and audiences.
Usage: python manage.py seed_domains
"""

from django.core.management.base import BaseCommand
from apps.core.services import DomainService, NicheService, AudienceService
from apps.core.mongodb import count_documents, delete_many, COLLECTIONS


class Command(BaseCommand):
    help = 'Seed database with domains, niches, and audiences'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding domains, niches, and audiences...'))
        
        # Check if already seeded
        domain_count = count_documents(COLLECTIONS['DOMAINS'], {})
        if domain_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠ Database already has {domain_count} domains'))
            confirm = input('Do you want to reseed? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Seeding cancelled'))
                return
            else:
                # Delete existing data
                self.stdout.write('Clearing existing data...')
                delete_many(COLLECTIONS['DOMAINS'], {})
                delete_many(COLLECTIONS['NICHES'], {})
                delete_many(COLLECTIONS['AUDIENCES'], {})
                self.stdout.write(self.style.SUCCESS('  ✓ Cleared existing data'))
        
        # Seed Domains
        self.stdout.write('Creating domains...')
        domains_data = self.get_domains_data()
        domain_ids = {}
        
        for domain_data in domains_data:
            domain_id = DomainService.create_domain(domain_data)
            domain_ids[domain_data['name']] = domain_id
            self.stdout.write(self.style.SUCCESS(f'  ✓ {domain_data["name"]}'))
        
        # Seed Niches
        self.stdout.write('\nCreating niches...')
        niches_data = self.get_niches_data(domain_ids)
        NicheService.create_niches_bulk(niches_data)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(niches_data)} niches'))
        
        # Seed Audiences
        self.stdout.write('\nCreating audiences...')
        audiences_data = self.get_audiences_data(domain_ids)
        AudienceService.create_audiences_bulk(audiences_data)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(audiences_data)} audiences'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Seeding complete!'))
        self.stdout.write(f'   Domains: {len(domains_data)}')
        self.stdout.write(f'   Niches: {len(niches_data)}')
        self.stdout.write(f'   Audiences: {len(audiences_data)}')
    
    def get_domains_data(self):
        """Get domain seed data based on subscription plans"""
        return [
            {
                'name': 'Artificial Intelligence & Machine Learning',
                'description': 'AI technologies, machine learning algorithms, and intelligent systems',
                'icon': '🤖',
                'subscription_tiers': ['creator', 'enterprise'],
            },
            {
                'name': 'Automation Workflows',
                'description': 'Process automation, workflow optimization, and productivity tools',
                'icon': '⚙️',
                'subscription_tiers': ['creator', 'enterprise'],
            },
            {
                'name': 'Health & Wellness Technology',
                'description': 'Digital health solutions, wellness apps, and medical technology',
                'icon': '🏥',
                'subscription_tiers': ['creator', 'enterprise'],
            },
            {
                'name': 'Cyber-security',
                'description': 'Information security, data protection, and threat prevention',
                'icon': '🔐',
                'subscription_tiers': ['creator', 'enterprise'],
            },
            {
                'name': 'Creator Economy & Digital Content',
                'description': 'Content creation, digital media, and creator monetization',
                'icon': '🎬',
                'subscription_tiers': ['creator', 'enterprise'],
            },
            {
                'name': 'Web3 & Blockchain',
                'description': 'Decentralized technologies, cryptocurrencies, and blockchain applications',
                'icon': '⛓️',
                'subscription_tiers': ['enterprise'],
            },
            {
                'name': 'E-commerce & Retail Tech',
                'description': 'Online retail, shopping technology, and digital commerce',
                'icon': '🛒',
                'subscription_tiers': ['enterprise'],
            },
            {
                'name': 'Data Analytics & Business Intelligence',
                'description': 'Data analysis, business insights, and analytics tools',
                'icon': '📊',
                'subscription_tiers': ['creator', 'enterprise'],
            },
            {
                'name': 'Gaming & Interactive Entertainment',
                'description': 'Video games, interactive media, and entertainment technology',
                'icon': '🎮',
                'subscription_tiers': ['enterprise'],
            },
            {
                'name': 'Kids & Parenting',
                'description': 'Children education, parenting guides, and family content',
                'icon': '👨‍👩‍👧‍👦',
                'subscription_tiers': ['personal', 'creator', 'enterprise'],
            },
            {
                'name': 'Nutrition & Meditation',
                'description': 'Health nutrition, mindfulness, and wellness practices',
                'icon': '🧘',
                'subscription_tiers': ['personal', 'enterprise'],
            },
            {
                'name': 'Recipes & Cooking',
                'description': 'Culinary recipes, cooking techniques, and food preparation',
                'icon': '👨‍🍳',
                'subscription_tiers': ['personal', 'creator', 'enterprise'],
            },
        ]
    
    def get_niches_data(self, domain_ids):
        """Get niche seed data for each domain - EXACTLY as specified in project requirements"""
        niches = []
        
        # Artificial Intelligence & Machine Learning
        niches.extend([
            {'name': 'Generative AI tools and applications', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'AI prompt engineering and optimization', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'AI safety and alignment research', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'Custom GPT development', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'AI-powered automation solutions', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'Machine learning operations (MLOps)', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'Computer vision applications', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'Natural language processing tools', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
        ])
        
        # Automation Workflows
        niches.extend([
            {'name': 'n8n & Open-Source Workflow Automation', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'AI-Enhanced Automation', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'SMB / Freelancer Process Automation', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'Automation as a Service (AaaS)', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'IoT + Industrial Automation (no-code integrations)', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'Workflow Analytics & Monitoring', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'Automation Education & Templates Marketplaces', 'domain_id': domain_ids['Automation Workflows']},
        ])
        
        # Health & Wellness Technology
        niches.extend([
            {'name': 'Mental health apps and teletherapy platforms', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Wearable health device integration', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Personalized nutrition and meal planning', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Sleep optimization technology', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Fitness tracking and virtual coaching', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Preventive healthcare solutions', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Biohacking and longevity tech', 'domain_id': domain_ids['Health & Wellness Technology']},
        ])
        
        # Cyber-security
        niches.extend([
            {'name': 'Zero-trust security architecture', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Identity and access management', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Cloud security solutions', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Ransomware protection', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Privacy-focused tools', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Security awareness training platforms', 'domain_id': domain_ids['Cyber-security']},
        ])
        
        # Creator Economy & Digital Content
        niches.extend([
            {'name': 'Content monetization platforms', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Creator management tools', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Short-form video editing software', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Live streaming technology', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Digital asset management', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Influencer marketing platforms', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Podcast production and distribution', 'domain_id': domain_ids['Creator Economy & Digital Content']},
        ])
        
        # Web3 & Blockchain
        niches.extend([
            {'name': 'Decentralized finance (DeFi) applications', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'NFT utility platforms (beyond art)', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'Blockchain supply chain solutions', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'Digital identity verification', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'Cryptocurrency payment processors', 'domain_id': domain_ids['Web3 & Blockchain']},
        ])
        
        # E-commerce & Retail Tech
        niches.extend([
            {'name': 'Social commerce integration', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'AI-powered personalization', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Augmented reality shopping experiences', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Subscription box services', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Direct-to-consumer (D2C) brands', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Resale and secondhand marketplaces', 'domain_id': domain_ids['E-commerce & Retail Tech']},
        ])
        
        # Data Analytics & Business Intelligence
        niches.extend([
            {'name': 'Real-time analytics dashboards', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'Predictive analytics tools', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'Customer data platforms', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'Data visualization software', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'Market intelligence solutions', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
        ])
        
        # Gaming & Interactive Entertainment
        niches.extend([
            {'name': 'Cloud gaming platforms', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Mobile gaming monetization', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Game development tools', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Esports infrastructure', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Virtual reality gaming experiences', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
        ])
        
        # Kids & Parenting
        niches.extend([
            {'name': 'Bedtime Stories & Audio Tales', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Pre-School Apprenticeship / Early Learning Skills', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Grammar, Alphabets & Early Language Learning', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Math through Stories & Games', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Religion, Cultures & Moral Understanding', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Curiosity-Based Learning ("Why?" Series)', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Soft Skills & Emotional Intelligence (EQ)', 'domain_id': domain_ids['Kids & Parenting']},
        ])
        
        # Nutrition & Meditation
        niches.extend([
            {'name': 'Meditation & Mindfulness', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Yoga & Body Awareness', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Nutrition Fundamentals for Healthy Living', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Ingredient Education & Smart Eating', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Mind–Body Connection', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Concentration & Focus Practices', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Cultural & Spiritual Nutrition Practices', 'domain_id': domain_ids['Nutrition & Meditation']},
        ])
        
        # Recipes & Cooking
        niches.extend([
            {'name': 'cooking-tech', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'smart appliances', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'IoT cooking devices', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'Food content + niche cuisine', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'recipes trends', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'Health-focused cooking', 'domain_id': domain_ids['Recipes & Cooking']},
        ])
        
        return niches
    
    def get_audiences_data(self, domain_ids):
        """Get audience seed data - EXACTLY as specified in project requirements"""
        audiences = []
        
        # Artificial Intelligence & Machine Learning audiences
        audiences.extend([
            {'name': 'Tech Professionals & Developers', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'Entrepreneurs & Founders', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'Business Executives & Managers', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'Students & Lifelong Learners', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
            {'name': 'General Public (Intro-level "AI for Everyone")', 'domain_id': domain_ids['Artificial Intelligence & Machine Learning']},
        ])
        
        # Automation Workflows audiences
        audiences.extend([
            {'name': 'Entrepreneurs & Founders (process automation)', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'Freelancers / SMB Owners', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'Tech Professionals (developers, system integrators)', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'Agencies offering AaaS services', 'domain_id': domain_ids['Automation Workflows']},
            {'name': 'Students (learning automation concepts)', 'domain_id': domain_ids['Automation Workflows']},
        ])
        
        # Health & Wellness Technology audiences
        audiences.extend([
            {'name': 'Health & Fitness Enthusiasts', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Medical & Wellness Professionals', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Entrepreneurs (HealthTech founders)', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'General Public (interested in modern wellness)', 'domain_id': domain_ids['Health & Wellness Technology']},
            {'name': 'Students (health science / tech)', 'domain_id': domain_ids['Health & Wellness Technology']},
        ])
        
        # Cyber-security audiences
        audiences.extend([
            {'name': 'IT & Security Professionals', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Business Executives (risk management)', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Entrepreneurs (SMB protection)', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'Students (learning cybersecurity)', 'domain_id': domain_ids['Cyber-security']},
            {'name': 'General Public (privacy education)', 'domain_id': domain_ids['Cyber-security']},
        ])
        
        # Creator Economy & Digital Content audiences
        audiences.extend([
            {'name': 'Content Creators & Influencers', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Digital Marketers', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Entrepreneurs / Startup Founders', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Agencies & Social Media Managers', 'domain_id': domain_ids['Creator Economy & Digital Content']},
            {'name': 'Students (media & communication)', 'domain_id': domain_ids['Creator Economy & Digital Content']},
        ])
        
        # Web3 & Blockchain audiences
        audiences.extend([
            {'name': 'Crypto Enthusiasts', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'Blockchain Developers', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'Entrepreneurs & Founders', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'Investors & Analysts', 'domain_id': domain_ids['Web3 & Blockchain']},
            {'name': 'Students (finance & technology)', 'domain_id': domain_ids['Web3 & Blockchain']},
        ])
        
        # E-commerce & Retail Tech audiences
        audiences.extend([
            {'name': 'E-commerce Entrepreneurs & Sellers', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Marketers & Brand Managers', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Business Executives', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Students (business / marketing)', 'domain_id': domain_ids['E-commerce & Retail Tech']},
            {'name': 'Tech Enthusiasts (retail innovation)', 'domain_id': domain_ids['E-commerce & Retail Tech']},
        ])
        
        # Data Analytics & Business Intelligence audiences
        audiences.extend([
            {'name': 'Business Analysts & Data Scientists', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'Executives / Decision Makers', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'Entrepreneurs', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'Students (data / business)', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
            {'name': 'General Readers (data literacy)', 'domain_id': domain_ids['Data Analytics & Business Intelligence']},
        ])
        
        # Gaming & Interactive Entertainment audiences
        audiences.extend([
            {'name': 'Gamers & eSports Fans', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Game Developers & Designers', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Streamers & Creators', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Tech Enthusiasts', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
            {'name': 'Students (game design / digital media)', 'domain_id': domain_ids['Gaming & Interactive Entertainment']},
        ])
        
        # Kids & Parenting audiences
        audiences.extend([
            {'name': 'Parents & Families', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Educators & Teachers', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Child Psychologists / Parenting Coaches', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Early Childhood Centers / Schools', 'domain_id': domain_ids['Kids & Parenting']},
            {'name': 'Students (education / pedagogy)', 'domain_id': domain_ids['Kids & Parenting']},
        ])
        
        # Nutrition & Meditation audiences
        audiences.extend([
            {'name': 'Health & Wellness Enthusiasts', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'General Public (seeking balance)', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Educators & Trainers', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Yoga / Meditation Practitioners', 'domain_id': domain_ids['Nutrition & Meditation']},
            {'name': 'Parents (teaching mindfulness to families)', 'domain_id': domain_ids['Nutrition & Meditation']},
        ])
        
        # Recipes & Cooking audiences
        audiences.extend([
            {'name': 'Home Cooks & Food Enthusiasts', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'Health-conscious Readers', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'Culinary Students / Chefs', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'Parents & Families', 'domain_id': domain_ids['Recipes & Cooking']},
            {'name': 'Content Creators (food bloggers, YouTubers)', 'domain_id': domain_ids['Recipes & Cooking']},
        ])
        
        return audiences
