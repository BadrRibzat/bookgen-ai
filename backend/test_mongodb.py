import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print("Testing MongoDB Connection...")
print(f"MONGODB_CLIENT: {settings.MONGODB_CLIENT}")
print(f"MONGODB_DATABASE: {settings.MONGODB_DATABASE}")

if settings.MONGODB_CLIENT:
    try:
        # Test the connection
        settings.MONGODB_CLIENT.admin.command('ping')
        print("✅ MongoDB connection test: PASSED")
        
        # List databases to verify access
        dbs = settings.MONGODB_CLIENT.list_database_names()
        print(f"Available databases: {dbs}")
        
    except Exception as e:
        print(f"❌ MongoDB connection test failed: {e}")
else:
    print("❌ MongoDB client not available")
