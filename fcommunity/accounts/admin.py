# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from accounts.models import CompetitionProfile, TeamProfile, UserProfile

# Register your models here.
class TeamProfileAdmin(admin.ModelAdmin):
    model = TeamProfile
    filter_horizontal = ('comps',)
admin.site.register(CompetitionProfile)
admin.site.register(TeamProfile, TeamProfileAdmin)
admin.site.register(UserProfile)