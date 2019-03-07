from django.contrib import admin

from web.output.models import RSSOutput


# Register your models here.
@admin.register(RSSOutput)
class RSSOutputAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RSSOutput._meta.fields]
