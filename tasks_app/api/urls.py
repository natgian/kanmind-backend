from django.urls import path, include
from rest_framework import routers
from .views import CommentViewSet, TaskViewSet

router = routers.SimpleRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
  path("tasks/<int:task_id>/comments/", CommentViewSet.as_view({"post": "create", "get": "list"})),
  path("tasks/<int:task_id>/comments/<int:pk>/", CommentViewSet.as_view({"delete": "destroy"})),
  path("", include(router.urls))
]