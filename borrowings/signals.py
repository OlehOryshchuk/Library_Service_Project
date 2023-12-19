import os
import dotenv
import asyncio

from django.conf import settings
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
            "NEW BORROWING!!!\n"
            f"Book title: {instance.book.title}\n"
            f"Book author: {instance.book.author}\n"
            f"Borrowing date: {instance.borrow_date}\n"
            f"Expected return date: {instance.expected_return_date}\n"
        )
        asyncio.run(send_telegram_notification(
            bot_token=settings.TELEGRAM_BOT_TOKEN,
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=message
        ))
