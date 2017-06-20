from django.contrib import admin

from events.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'privacy', 'views')

admin.site.register(Event, EventAdmin)
