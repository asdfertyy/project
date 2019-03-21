# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from accounts.models import CompetitionProfile, TeamProfile, UserProfile, GroundProfile, Match, Result, Comment

# Register your models here.
class TeamProfileAdmin(admin.ModelAdmin):
    model = TeamProfile
    filter_horizontal = ('comps',)
admin.site.register(CompetitionProfile)
admin.site.register(TeamProfile, TeamProfileAdmin)
admin.site.register(UserProfile)
admin.site.register(GroundProfile)
admin.site.register(Match)
admin.site.register(Result)
admin.site.register(Comment)


class RentalAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
