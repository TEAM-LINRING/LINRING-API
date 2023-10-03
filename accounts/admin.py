from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt import token_blacklist

from accounts.models import User, TagSet


# Register your models here.
@admin.register(User)
class UserAdmin(ModelAdmin):
    base_model = User
    list_display = [field.name for field in User._meta.fields]
    search_fields = ["email"]

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(is_superuser=False)

    def save_model(self, request, obj, form, change):
        try:
            user_database = User.objects.get(pk=obj.pk)
            # Check firs the case in which the password is not encoded, then check in the case that the password is encode
            if not (check_password(form.data['password'], user_database.password) or
                    user_database.password == form.data['password']):
                obj.password = make_password(obj.password)
            else:
                obj.password = user_database.password
            # obj.username = user_database.username
        except Exception as e:
            print(e)
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)


class OutstandingTokenAdmin(token_blacklist.admin.OutstandingTokenAdmin):
    def get_readonly_fields(self, *args, **kwargs):
        return []

    def has_delete_permission(self, *args, **kwargs):
        return True  # or whatever logic you want

    def has_change_permission(self, request, obj=None):
        return True

    actions = ()


admin.site.unregister(token_blacklist.models.OutstandingToken)
admin.site.register(token_blacklist.models.OutstandingToken, OutstandingTokenAdmin)


@admin.register(TagSet)
class TagSetAdmin(ModelAdmin):
    base_model = TagSet
    list_display = [field.name for field in TagSet._meta.fields]
