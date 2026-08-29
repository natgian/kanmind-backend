from django.contrib import admin
from .models import Comment, Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
  """Configuration for Task interface in admin panel."""
  list_display = ("id", "board", "title", "status", "priority", "assignee", "reviewer", "due_date")
  list_select_related = ("board", "assignee", "reviewer")
  list_display_links = ("id", "title")
  list_filter = ("board", "status", "priority", "due_date", "assignee", "reviewer")
  search_fields = ("title", "description", "assignee__fullname", "reviewer__fullname")
  ordering = ("due_date", )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
  """Configuration for Comment interface in admin panel."""
  list_display = ("id", "author", "task", "created_at")
  list_select_related = ("author", "task")
  list_display_links = ("id", "task")
  list_filter = ("author", "created_at")
  search_fields = ("author__fullname", "task__title", "content")
  ordering = ("-created_at",)