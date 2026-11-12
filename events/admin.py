from django.contrib import admin
from .models import Event, EventParticipant


class ParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 0
    readonly_fields = ("registered_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    inlines = [ParticipantInline]


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "event", "registered_at")
    list_filter = ("event",)