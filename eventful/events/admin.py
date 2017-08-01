from django.contrib import admin

from .models import Event, EventInvite


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_date', 'privacy', 'views')


class EventInviteAdmin(admin.ModelAdmin):
    list_display = ('event', 'from_user', 'to_user', 'status')


admin.site.register(Event, EventAdmin)
admin.site.register(EventInvite, EventInviteAdmin)
