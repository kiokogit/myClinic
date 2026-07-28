from django.apps import AppConfig


class AclConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'acl'

    def ready(self):
        import utils.auth_classes  # noqa: F401 
