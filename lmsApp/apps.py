import importlib
from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_initial_data(sender, **kwargs):
    ModelName = sender.get_model('Category')
    ModelName.objects.get_or_create(id="1", name="சங்க இலக்கியம்")
    ModelName.objects.get_or_create(id="2", name="அற இலக்கியம்")
    ModelName.objects.get_or_create(id="3", name="காப்பிய இலக்கியம்")
    ModelName.objects.get_or_create(id="4", name="பக்தி இலக்கியம்")
    ModelName.objects.get_or_create(id="5", name="சிற்றிலக்கியம்")
    ModelName.objects.get_or_create(id="6", name="நாட்டுப்புறவியல்")
    ModelName.objects.get_or_create(id="7", name="இக்கால இலக்கியம்")
    ModelName.objects.get_or_create(id="8", name="மொழிபெயர்ப்பு")
    ModelName.objects.get_or_create(id="9", name="பொதுவானவை")

class lmsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lmsApp'

    def ready(self):
        post_migrate.connect(create_initial_data, sender=self)
