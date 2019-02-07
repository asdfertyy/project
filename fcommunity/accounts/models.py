# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

# Create your models here.
class CompetitionProfile(models.Model):
    comp_id = models.AutoField(primary_key=True)
    comp_name = models.CharField(max_length = 30)
    comp_type = models.IntegerField(default = 0)
    comp_teamsize = models.IntegerField(default = 5)
    comp_squadsize = models.IntegerField(default = 10)
    comp_start_date = models.DateField(blank = True, default = datetime.date.today)
    comp_end_date = models.DateField(blank = True, default = datetime.date.today)

    def __str__(self):
        return self.comp_name


class TeamProfile(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length = 30)
    team_date_formed = models.DateField(blank = True, default = datetime.date.today)
    team_matches_played = models.IntegerField(default = 0)
    team_wins = models.IntegerField(default = 0)
    team_type = models.IntegerField(default = 0)
    team_draws = models.IntegerField(default = 0)
    team_losses = models.IntegerField(default = 0)
    team_address = models.CharField(max_length = 100, default = '')
    team_description = models.CharField(max_length = 250, default = '')
    comps = models.ManyToManyField(CompetitionProfile)


    def __str__(self):
        return self.team_name
    #
    # class Meta:
    #     ordering = ('team_name',)



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    description = models.CharField(max_length = 250, default = '')
    address = models.CharField(max_length = 100, default = '')
    birthday = models.DateField(blank = True, default = datetime.date.today)
    teams = models.ForeignKey(TeamProfile, on_delete=models.PROTECT, null = True, default = 1)

    objects = models.Manager()




    def __str__(self):
        return self.user.username

    def create_profile(sender, **kwargs):
        if kwargs['created']:
            user_profile = UserProfile.objects.create(user=kwargs['instance'])

    post_save.connect(create_profile, sender=User)