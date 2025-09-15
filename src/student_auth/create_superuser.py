import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()

USERNAME = os.getenv("ADMIN_USERNAME", "admin")
EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminPass123!")

user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={
        "email": EMAIL,
        "is_staff": True,
        "is_superuser": True,
    },
)

# Always (re)set password to ensure access
user.email = EMAIL
user.is_staff = True
user.is_superuser = True
user.set_password(PASSWORD)
user.save()

print(("Created" if created else "Updated"), "superuser:", USERNAME)