from django.contrib import admin

from userprofiles.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_display = ('user', 'website')


admin.site.register(UserProfile, UserProfileAdmin)
