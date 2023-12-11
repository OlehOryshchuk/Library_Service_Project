from rest_framework.routers import DefaultRouter

from .views import BorrowingViewSet

router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = router.urls

app_name = "borrowings"
