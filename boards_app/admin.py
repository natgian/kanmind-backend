from django.contrib import admin
from .models import Board

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
  list_display = ("id", "title", "owner")
  list_select_related = ("owner",) 
  list_display_links = ("id", "title") 
  list_filter = ("owner",)
  search_fields = ("title",)
  ordering = ("title",)
  autocomplete_fields = ('members',)


