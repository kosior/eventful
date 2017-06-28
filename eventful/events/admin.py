from django.contrib import admin

from events.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_date', 'privacy', 'views')

admin.site.register(Event, EventAdmin)
