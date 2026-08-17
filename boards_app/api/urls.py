from django.urls import path, include
from rest_framework import routers
from .views import BoardViewSet

router = routers.SimpleRouter()
router.register(r"boards", BoardViewSet)

urlpatterns = router.urls