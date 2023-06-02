from django.contrib import admin
from users.models import Follow, User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role')
    list_filter = ('email', 'first_name')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
