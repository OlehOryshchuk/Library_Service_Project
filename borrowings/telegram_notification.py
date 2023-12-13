import requests


def send_telegram_notification(bot_token: str, chat_id: str, text: str):
    """
    Send notification on telegram chat_id using bot_token
    """
    return requests.get(
        (
            f"https://api.telegram.org/bot{bot_token}/"
            f"sendMessage?chat_id={chat_id}&text={text}"
        )
    )
