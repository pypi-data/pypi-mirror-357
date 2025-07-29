import requests
from .models import GreenlightConfig

def send_discord_message(color):
    config = GreenlightConfig.objects.first()
    if not config:
        print("No GreenlightConfig found.")
        return

    messages = {
        "green": config.green_message,
        "yellow": config.yellow_message,
        "red": config.red_message,
    }

    content = messages.get(color, f"⚪ Unknown alert: {color}")

    if config.discord_webhook:
        response = requests.post(config.discord_webhook, json={"content": content})
        print(f"Discord response: {response.status_code} - {response.text}")
    else:
        print("No Discord webhook configured.")

