from django.contrib.auth.models import Group
from django.contrib import admin

from .models import Book

admin.site.unregister(Group)
admin.site.register(Book)
