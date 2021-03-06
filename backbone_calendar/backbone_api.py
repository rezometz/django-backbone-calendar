import dateutil
from dateutil import parser as date_parser

from django.forms import widgets
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

import backbone

from .models import Event
from .forms import EventForm


class EventApiView(backbone.views.BackboneAPIView):
    model = Event
    form = EventForm
    display_fields = (
        'title', 'start', 'end', 'agenda',
        'places', 'allDay', 'url',
    )

    def get(self, request, id=None, **kwargs):
        error_dates = '`start` and `end` parameters are both required.'
        
        if not id:
            self.start = date_parser.parse(self.request.GET.get('start'))
            self.end = date_parser.parse(self.request.GET.get('end'))

            if not self.start or not self.end:
                return HttpResponseBadRequest(_(
                    'Invalid_request : %(error)s' % (error_dates)
                ))
        return super(EventApiView, self).get(request, id, **kwargs)

    def queryset(self, request):
        qs = super(EventApiView, self).queryset(request)

        if request.method == 'GET':
            places = map(int, self.request.GET.getlist('places[]', []))
            agendas = map(int, self.request.GET.getlist('agendas[]', []))

            filter  = Q(start__gte=self.start, start__lte=self.end)
            filter |= Q(  end__gte=self.start,   end__lte=self.end)

            if len(places) > 0:
                filter &= Q(places__in=places)

            if len(agendas) > 0:
                filter &= Q(agenda__in=agendas)

            qs = qs.filter(filter)

        return qs


backbone.site.register(EventApiView)
