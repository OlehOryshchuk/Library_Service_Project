import asyncio
from celery import shared_task
from .overdue_borrowing_scraper import async_overdue_borrowing_notification


@shared_task
def initiate_notify_overdue_borrowings():
    asyncio.run(async_overdue_borrowing_notification())
