from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.hashers import check_password, make_password

from accounts.models import User
from .models import Room, Message


# Register your models here.
@admin.register(Room)
class RoomAdmin(ModelAdmin):
    base_model = Room
    list_display = [field.name for field in Room._meta.fields]


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    base_model = Message
    list_display = ['id', 'room', 'sender', 'receiver', 'is_read', 'type', 'args', 'message']
    search_fields = ["sender__email", "receiver__email"]
