import asyncio

from django.conf import settings

from borrowings.telegram_notification import (
    send_telegram_notification
)
from borrowings.models import Borrowing


def send_success_payment_notification(borrowing: Borrowing):
    """Send Telegram successful payment message"""
    book = borrowing.book
    price_no_fines = borrowing.num_of_borrowing_days() * book.daily_fee
    price_with_fines = price_no_fines + (
            (borrowing.num_of_overdue_days() * book.daily_fee)
            * settings.FINE_MULTIPLIER
    )
    user = borrowing.user

    message = f"""
SUCCESS PAYMENT !!!!
Price without fines: {price_no_fines}$
Price with fines: {price_with_fines}$
Book title: {book.title}
Book author: {book.author}
Borrower id: {user.id}
    """

    return asyncio.run(send_telegram_notification(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
        chat_id=settings.TELEGRAM_CHAT_ID,
        text=message
    ))
