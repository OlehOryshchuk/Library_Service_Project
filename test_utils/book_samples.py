from books.models import Book


def book_sample(title: str, **param) -> Book:
    """Function for tests, returns Book instance"""
    default = {
        "title": title,
        "author": "Anon",
        "cover": "HARD",
        "inventory": 5,
        "daily_fee": 5,
    }

    default.update(**param)

    return Book.objects.create(**default)
