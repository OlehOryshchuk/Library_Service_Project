from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
)
from borrowings.models import Borrowing

from test_utils.book_samples import book_sample
from test_utils.borrowing_samples import borrowing_sample
from test_utils.main_test_utils import (
    expect_data_pagination_or_not,
    detail_url,
)


BORROWING_LIST_URL = reverse("borrowings:borrowing-list")


def return_borrowing(borrowing_id: id):
    return reverse("borrowings:borrowing-return", args=[borrowing_id])


def add_additional_fields(borrowing: Borrowing, **kwargs):
    """Add additional fields to borrowing instance"""
    for key, value in kwargs.items():
        setattr(borrowing, key, value)
    borrowing.save()
    return borrowing


class UnauthenticatedApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_method_auth_required(self):
        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_method_auth_required(self):
        res = self.client.get(detail_url("borrowing", 1))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_method_auth_required(self):
        res = self.client.post(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Main@gmail.com", password="rvtquen"
        )
        self.client.force_authenticate(self.user)

    def request_object(self):
        res = self.client.get(BORROWING_LIST_URL)
        return res.wsgi_request

    def create_user_and_borrowings(self, email, password, book_names):
        user = get_user_model().objects.create_user(email=email, password=password)
        for book_name in book_names:
            borrowing_sample(
                book=book_sample(book_name),
                user=user,
                request=self.request_object()
            )
        return user

    def get_user_borrowings(self, user):
        return Borrowing.objects.filter(user=user)

    def test_create_borrowing(self):
        data = {
            "expected_return_date": date.today(),
            "book": book_sample("Create Book").id,
        }

        res = self.client.post(BORROWING_LIST_URL, data)
        # After creation it redirects on Stripe hosted payment Session
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def assertEqualBorrowings(self, response, user, is_active=None):
        borrowings = self.get_user_borrowings(user)

        if is_active is not None:
            borrowings = borrowings.filter(actual_return_date__isnull=is_active)

        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
            context={"request": response.wsgi_request}
        )
        data = expect_data_pagination_or_not(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, serializer.data)

    def test_borrowings_list(self):
        self.create_user_and_borrowings(
            "TestUser@gmail.com", "rvtquen", ["Test1", "Test2"]
        )
        self.create_user_and_borrowings(
            "TestUser2@gmail.com", "rvtquen", ["Test3", "Test4"]
        )

        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqualBorrowings(res, self.user)

    def test_filter_borrowings_list_by_is_active_equal_true(self):
        self.create_user_and_borrowings(
            "TestUser@gmail.com", "rvtquen", ["Test1", "Test2"]
        )

        res = self.client.get(BORROWING_LIST_URL, {"is_active": "True"})
        self.assertEqualBorrowings(res, self.user, is_active=True)

    def test_filter_borrowings_list_by_is_active_equal_false(self):
        self.create_user_and_borrowings(
            "TestUser@gmail.com", "rvtquen", ["Test1", "Test2"]
        )

        res = self.client.get(BORROWING_LIST_URL, {"is_active": "False"})
        self.assertEqualBorrowings(res, self.user, is_active=False)

    def test_filter_borrowings_list_by_user_id_not_available(self):
        user2 = self.create_user_and_borrowings(
            "TestUser2@gmail.com", "rvtquen", ["Test1", "Test2"]
        )

        res = self.client.get(BORROWING_LIST_URL, {"user_id": user2.id})
        self.assertEqualBorrowings(res, self.user)

    def test_get_detail_borrowing(self):
        borrowing = borrowing_sample(
            book=book_sample("Detail Book"),
            user=self.user,
            request=self.request_object()
        )
        borrowing = add_additional_fields(
            borrowing=borrowing,
            payment_status="PENDING",
            fine_status=None,
        )

        res = self.client.get(detail_url("borrowing", borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = BorrowingDetailSerializer(
            borrowing,
            context={"request": res.wsgi_request}
        )
        res_data = expect_data_pagination_or_not(res.data)

        self.assertEqual(res_data, serializer.data)

    def test_return_borrowing(self):
        borrowing = borrowing_sample(
            book=book_sample("Detail Book"),
            user=self.user,
            request=self.request_object()
        )
        borrowing = add_additional_fields(
            borrowing=borrowing,
            payment_status="PENDING",
            fine_status=None,
        )

        res = self.client.post(return_borrowing(borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        borrowing.refresh_from_db()
        serializer = BorrowingDetailSerializer(
            borrowing,
            context={"request": res.wsgi_request}
        )
        res_data = expect_data_pagination_or_not(res.data)
        # print(res_data, serializer.data)
        self.assertEqual(res_data, serializer.data)

    def test_return_borrowing_twice_expect_error(self):
        borrowing = borrowing_sample(
            book=book_sample("Detail Book"),
            user=self.user,
            request=self.request_object()
        )
        self.client.post(return_borrowing(borrowing.id))
        res = self.client.post(return_borrowing(borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing_increased_book_inventory(self):
        inv_number = 10
        borrowing = borrowing_sample(
            book=book_sample("Detail Book", inventory=inv_number),
            user=self.user,
            request=self.request_object()
        )
        res = self.client.post(return_borrowing(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        borrowing.refresh_from_db()
        self.assertNotEqual(inv_number, borrowing.book.inventory)
        self.assertEqual(inv_number + 1, borrowing.book.inventory)


class AdminApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="test@gmai.com", password="rvtafj", is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def request_object(self):
        res = self.client.get(BORROWING_LIST_URL)
        return res.wsgi_request

    def test_admin_can_filter_borrowings_by_user_id(self):
        user2 = get_user_model().objects.create_user(
            email="TestUser@gmail.com", password="retvryojsp"
        )
        borrowing1 = borrowing_sample(
            book=book_sample("User2 Book"),
            user=user2,
            request=self.request_object(),
        )
        borrowing2 = borrowing_sample(
            book=book_sample("User Book"),
            user=self.admin,
            request=self.request_object(),
        )

        res = self.client.get(BORROWING_LIST_URL, {"user_id": user2.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        borrowings = Borrowing.objects.filter(user=user2)
        for borrowing in borrowings:
            add_additional_fields(
                borrowing=borrowing,
                payment_status="PENDING",
                fine_status=None,
            )

        serializer = BorrowingListSerializer(
            borrowings,
            many=True,
            context={"request": res.wsgi_request}
        )

        res_data = expect_data_pagination_or_not(res.data)
        self.assertEqual(res_data, serializer.data)

    def test_admin_can_get_borrowings_list(self):
        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_can_create_borrowing(self):
        data = {
            "expected_return_date": date.today(),
            "book": book_sample("Admin Create Book").id,
        }

        res = self.client.post(BORROWING_LIST_URL, data)
        # After creation it redirects on Stripe hosted payment Session
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_admin_can_get_detail_borrowing(self):
        borrowing = borrowing_sample(
            book=book_sample("Admin Detail Book"),
            user=self.admin,
            request=self.request_object()
        )
        res = self.client.get(detail_url("borrowing", borrowing.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
