## Library Service API

![Django](https://img.shields.io/badge/Django-4.2.8-brightgreen.svg)
![Django Rest Framework](https://img.shields.io/badge/Django%20Rest%20Framework-3.14.0-blue.svg)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2.22.0-brightgreen.svg)

Social Media API is a web application built with Django REST Framework offering a platform
for upgrading library manual tracking to an online system for efficient book borrowings, user 
management, and payments. Enhancing the overall user experience.

## Features
* Unauthenticated users are not allowed to do anything
* For authenticated users are allowed listing books, borrowings, payments,
  creating new borrowings
* Superuser (admin, staff) have admin site http://localhost:8000/admin/ with full control
    and with full control on platform
* For Authentication system we are using REST framework JWT
* Integrated Stripe API, safe platform where user can pay for borrowing books and fees
* Integrated Celery for creating asynchronous tasks
* Celery Beat for creating scheduled asynchronous tasks, interface is available
    for admins on http://localhost:8000/admin/
* Also we are using Flower for monitoring and managing Celery clusters.
* We have Telegram Bot which send notification on channel about new borrowing, success payment,
    and overdue borrowings which needs to be payed. Telegram Channel invite link
    https://t.me/+UchisNw2zmM5YTEy
* In ./borrowings/overdue_borrowing.scraper.py we are using `async` and `await` syntax with
    asyncio API for enhancing performance of notifying users about overdue borrowings
* Using Django signals to send notification on Telegram channel for every new borrowing
* There is also different feature like searching/ordering/filtering lists of data
    which you can see on api docs
* One of filtering feature of Borrowing list of by `?is_active=True/False` parameter for filtering
   by active borrowings (still not returned and available for all users).And second parameter
   `?user_id=1` (available only for admin users) returns user borrowings
* API documentation  http://127.0.0.1:8000/api/doc/swagger/
* Admin panel  http://localhost:8000/admin/

## Installation
1. Clone git repository to your local machine:
```
    https://github.com/OlehOryshchuk/Library_Service_Project.git
```
2. Copy the `.env.sample` file to `.env` and configure the environment variables
```
    cp .env.sample .env
```
3. Run command. Docker should be installed:
```
    docker-compose up --build
```
4. Access API as superuser you can use the following admin user account:

- **Email** admin@gmail.com : Email is not valid
- **Password** rtvlnoaola

### Usage
To access the API, navigate to http://localhost:8000/api/ in your web browser and enter one of endpoints.

### Endpoints
Library Service API endpoints 

bk_id - is the book integer id
- `/books/` - returns paginated list of books
- `/books/bk_id/` - book detail endpoint

Available only to admins:
- `/books/` - create book
- `/books/bk_id/` - update/delete book


br_id - is the borrowing integer id
- `/borrowings/` - return paginated list of user borrowings & to create new borrowing
- `/borrowings/br_id/` - borrowing detail data
- `/borrowings/br_id/renew_payment/` - updates the borrowing payments Stripe Session (
   they can expire)
- `/borrowings/br_id/return/` - return book increase inventory by 1 but if borrowing is 
  overdue (were not return it by borrowing.expected_return_day date) then redirect
  to Stripe Session page where user should pay fines for not returning in time

pay_id - is the payment integer id
- `/payments/` - return list of user payments
- `/payments/pay_id/` - return payment detail data
- `/payment/pay_id/success/` - Check if payment was paid if yes then we update the Payment
    status to `PAID`
- `/payment/pay_id/cancel/` - Just inform user about payment can be paid later with payment
    information

You can test Stripe Payment Session using tests data:
https://stripe.com/docs/testing?testing-method=card-numbers#visa

- `/users/register/` - incoming user can register himself
- `/users/token/` - authenticate user
- `/users/token/refresh/` - refresh JWT access token using refresh token
- `/users/token/verify/` - verify access token
- `/users/me/` - User manage endpoint

Admin (superuser) endpoint:
- `/admin/`

Documentation:
- `/doc/swagger/`: To access the API documentation, you can visit the interactive Swagger UI.
