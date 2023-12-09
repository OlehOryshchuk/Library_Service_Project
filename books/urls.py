from rest_framework.routers import DefaultRouter

from .views import BookViewSet

router = DefaultRouter()
router.register("books", BookViewSet)

urlpatterns = router.urls

app_name = "book"
