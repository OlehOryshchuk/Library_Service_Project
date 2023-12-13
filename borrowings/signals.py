import os

from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Borrowing
from .telegram_notification import send_telegram_notification


@receiver(post_save, sender=Borrowing)
def send_borrowing_notification(
        sender: post_save, instance: Borrowing, created: bool, **kwargs
):
    """Send telegram notification on every borrowing creation"""
    if created:
        message = (
            "NEW BORROWING!!!"
            f"Book title: {instance.book.title}"
            f"Book author: {instance.book.author}"
            f"Borrowing date: {instance.borrow_date}"
            f"Expected return date: {instance.expected_return_date}"
        )
        send_telegram_notification(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            text=message
        )
