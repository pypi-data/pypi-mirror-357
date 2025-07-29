from django.db import models

class GreenlightConfig(models.Model):
    name = models.CharField(max_length=100, default="default", unique=True)
    
    green_message = models.TextField(default="🟢 **GREEN ALERT!** All clear.")
    yellow_message = models.TextField(default="🟡 **YELLOW ALERT!** Be ready.")
    red_message = models.TextField(default="🔴 **RED ALERT!** Action needed!")

    discord_webhook = models.URLField(help_text="Paste the full Discord webhook URL here.")

    def __str__(self):
        return f"Greenlight Config: {self.name}"

    class Meta:
        permissions = [
            ("can_use_greenlight", "Can use Greenlight tool"),
        ]
