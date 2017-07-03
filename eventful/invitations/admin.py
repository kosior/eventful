from django.contrib import admin

from invitations.models import FriendInvitation, EventInvitation


admin.site.register(FriendInvitation)
admin.site.register(EventInvitation)
