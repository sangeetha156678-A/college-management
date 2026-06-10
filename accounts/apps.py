from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.db.models.signals import post_migrate

        from accounts.demo_users import ensure_demo_users_on_migrate

        post_migrate.connect(ensure_demo_users_on_migrate, sender=self)
