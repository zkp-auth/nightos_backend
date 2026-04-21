from rest_framework.routers import DefaultRouter
from .views import DJViewSet, GenreViewSet

router = DefaultRouter()
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"djs", DJViewSet, basename="dj")

urlpatterns = router.urls
