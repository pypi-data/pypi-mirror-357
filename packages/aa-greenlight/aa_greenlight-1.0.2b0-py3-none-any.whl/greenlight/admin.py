from django.contrib import admin
from .models import GreenlightConfig

@admin.register(GreenlightConfig)
class GreenlightConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'discord_webhook')
    fieldsets = (
        (None, {
            'fields': ('name', 'discord_webhook')
        }),
        ('Messages', {
            'fields': ('green_message', 'yellow_message', 'red_message'),
            'description': 'Customize messages sent per alert color.',
        }),
    )
