from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="nagababu",
                email="ballanagababu29@gmail.com",
                password="9014884200@Naga"
            )
            print("Superuser created")
        else:
            print("Superuser already exists")
