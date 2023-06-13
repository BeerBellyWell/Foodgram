from django.contrib import admin
from users.models import Follow, User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role')
    list_filter = ('email', 'first_name')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = (
        'user__username', 'user__email', 'following__username',
        'following__email'
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
