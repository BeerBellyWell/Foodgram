from django.contrib import admin
from users.models import (
    User, Follow
)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
