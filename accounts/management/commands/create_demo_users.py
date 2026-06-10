from django.core.management.base import BaseCommand

from accounts.demo_users import DEMO_USERS, ensure_demo_users


class Command(BaseCommand):
    help = 'Create demo users for admin, lecturer, and student login'

    def handle(self, *args, **options):
        ensure_demo_users()

        for data in DEMO_USERS:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Ready: "{data["username"]}" (role={data["role"]}, password={data["password"]})'
                )
            )

        self.stdout.write(self.style.SUCCESS('Demo users are ready.'))
