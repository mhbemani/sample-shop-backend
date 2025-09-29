# create_superuser.py
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop_backend.settings")
django.setup()

User = get_user_model()

# چک کن ببین superuser وجود داره یا نه
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
    print("Superuser created!")
else:
    print("Superuser already exists.")
