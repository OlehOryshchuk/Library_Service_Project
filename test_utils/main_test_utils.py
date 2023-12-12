from django.urls import reverse


def expect_data_pagination_or_not(data):
    """Return test response data with pagination or not"""
    if "results" in data:
        return data["results"]
    return data


def detail_url(view_name: str, borrowing_id: int):
    return reverse(f"borrowings:{view_name}-detail", args=[borrowing_id])
