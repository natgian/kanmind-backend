from django.urls import path, include
from rest_framework import routers
from .views import BoardViewSet, EmailCheckView

router = routers.SimpleRouter()
router.register(r"boards", BoardViewSet, basename="board")

urlpatterns = [
  path("", include(router.urls)),
  path("email-check/", EmailCheckView.as_view(), name="email-check")
]