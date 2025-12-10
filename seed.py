# seed.py

from app_factory import AppFactory
from seed.admin import seed_admin_user

print("🔧 Initializing app for seeding...")

# 1. Create app
factory = AppFactory()
app = factory.create_app()

# 2. Run seeding INSIDE app context
print("\n🔍 Seeding admin user...")
with app.app_context():
    seed_admin_user()

print("✅ Admin seed execution finished.")
