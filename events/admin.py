from django.contrib import admin

from events.models import EventTag, Event, Ticket, AssistanceOffer


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    pass


@admin.register(AssistanceOffer)
class AssistanceOfferAdmin(admin.ModelAdmin):
    pass
