from django.contrib import admin

# Register your models here.
from queryapp.models import Text, TextsAlias

admin.site.register(Text)
admin.site.register(TextsAlias)
