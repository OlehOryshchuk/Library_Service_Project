import asyncio
import os
from datetime import timedelta
import time
from functools import wraps

import dotenv

from asgiref.sync import sync_to_async, async_to_sync
from django.utils import timezone
from django.db.models import QuerySet
from .models import Borrowing

from .telegram_notification import send_telegram_notification

dotenv.load_dotenv()


def execution_time(func):
    """
    Display execution time of asynchronous function
    :param func:
    :return:
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()

        print(
            f"Elapsed time for {func.__name__} took {end - start} seconds"
        )
        return result
    return wrapper


async def overdue_day():
    return timezone.now().date() + timedelta(days=1)


@execution_time
async def get_overdue_borrowings():
    """
    Get overdue borrowings where expected_return_date
    is pass tomorrow date.
    Or no overdue send to telegram chat message about it
    """
    tomorrow = await overdue_day()
    overdue: QuerySet = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow,
        actual_return_date__isnull=True,
    )

    if not await overdue.aexists():
        return await send_telegram_notification(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            text=(
                "No borrowings overdue today!"
            )
        )
    return overdue


@execution_time
async def notify_overdue_borrowing(borrowing):
    """
    Send notification for a single overdue borrowing
    """
    days_overdue = await overdue_day() - borrowing.expected_return_date
    price_no_fines = borrowing.borrow_date - await overdue_day()
    book = await sync_to_async(getattr)(borrowing, "book")
    user = await sync_to_async(getattr)(borrowing, "user")
    message = f"""
OVERDUE BORROWING!!!!
Book daily fee: {book.daily_fee}$
Borrowed day: {borrowing.borrow_date}
Days overdue: {days_overdue.days}
Price without fine: {price_no_fines}$
Book title: {book.title}
Book author: {book.author}
Borrower id: {user.id}
    """

    # Schedule the async notification task
    return await send_telegram_notification(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        text=message
    )


@execution_time
async def notify_overdue_borrowings(
        borrowings_overdue: QuerySet[Borrowing]
):
    """
    Except Overdue Borrowings and send notification on telegram
    channel on each borrowing
    :param borrowings_overdue:
    :return:
    """
    if isinstance(borrowings_overdue, QuerySet):

        tasks = [
            notify_overdue_borrowing(borrowing)
            async for borrowing in borrowings_overdue
        ]

        # Run all the notification tasks concurrently
        await asyncio.gather(*tasks)


@execution_time
async def async_overdue_borrowing_notification():
    await notify_overdue_borrowings(await get_overdue_borrowings())
