import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

username = "GUSTAVOFREIRE"
email = "seuemail@email.com"
password = "123456"  # depois você troca

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser criado!")
else:
    print("Superuser já existe!")