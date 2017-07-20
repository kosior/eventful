from django.contrib import admin

from .models import UserProfile, FriendRequest


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_display = ('user', 'website')


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
