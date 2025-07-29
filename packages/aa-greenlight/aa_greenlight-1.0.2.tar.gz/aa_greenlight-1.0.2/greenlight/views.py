import requests
from .models import GreenlightConfig

def send_discord_message(color, user):
    config = GreenlightConfig.objects.first()
    if not config or not config.discord_webhook:
        return

    messages = {
        "green": config.green_message,
        "yellow": config.yellow_message,
        "red": config.red_message,
    }

    content = messages.get(color, f"⚪ Unknown alert: {color}")

    # Try to pull main character name from AllianceAuth
    if color in ["green", "yellow"]:
        try:
            character_name = user.profile.main_character.character_name
            content += f"\nFleet under: **{character_name}**"
        except Exception:
            content += "\nFleet under: [Unknown User]"

    requests.post(config.discord_webhook, json={"content": content})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('greenlight.can_use_greenlight', raise_exception=True)
def greenlight_view(request):
    if request.method == 'POST':
        color = request.POST.get('color')
        if color:
            send_discord_message(color, request.user)
        return redirect('greenlight')
    return render(request, 'greenlight/greenlight.html')
