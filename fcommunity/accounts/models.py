# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django_google_maps import fields as map_fields
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

# Create your models here.
class GroundProfile(models.Model):
    ground_id = models.AutoField(primary_key = True)
    ground_name = models.CharField(max_length = 30)
    ground_address = models.CharField(max_length=200)
    ground_latitude = models.DecimalField(max_digits=18, decimal_places=10, null=True)
    ground_longitude = models.DecimalField(max_digits=18, decimal_places=10, null=True)#, default = '')#[53.480614, -2.237503])
    ground_description = models.CharField(max_length = 250, default = '')
    is_it_paid = models.BooleanField(default = 0)

    def __str__(self):
        return self.ground_name

    # def save(self, *args, **kwargs):
    #     # If latlng has no value:
    #     if not self.latlng:
    #         # Add + between fields with values:
    #         location = '+'.join(
    #             filter(None, (self.address1, self.address2, self.city, self.state, self.zip, self.country)))
    #         # Attempt to get latitude/longitude from Google Geocoder service v.3:
    #         self.latlng = get_lat_lng(location)
    #     super(Place, self).save(*args, **kwargs)


class CompetitionProfile(models.Model):
    comp_id = models.AutoField(primary_key=True)
    comp_name = models.CharField(max_length = 30)
    comp_type = models.IntegerField(default = 0) # 0 - league; 1 - knockout, 1 leg; 2 - knockout, 2 legs
    comp_teamNumber = models.IntegerField(default = 5)
    comp_squadSize = models.IntegerField(default = 10)
    comp_start_date = models.DateField(blank = True, default = datetime.date.today)
    comp_end_date = models.DateField(blank = True, default = datetime.date.today)

    def __str__(self):
        return self.comp_name


class TeamProfile(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length = 30, default = 'https://cdn2.iconfinder.com/data/icons/ios-7-icons/50/football2-256.png')
    team_logo = models.URLField(null=True, max_length = 2000)
    team_date_formed = models.DateField(blank = True, default = datetime.date.today)
    team_matches_played = models.IntegerField(default = 0)
    team_wins = models.IntegerField(default = 0)
    team_type = models.IntegerField(default = 0)
    team_draws = models.IntegerField(default = 0)
    team_losses = models.IntegerField(default = 0)
    team_address = models.ForeignKey(GroundProfile, on_delete=models.CASCADE)
    team_description = models.CharField(max_length = 250, default = '')
    comps = models.ManyToManyField(CompetitionProfile)


    def __str__(self):
        return self.team_name
    #
    # class Meta:
    #     ordering = ('team_name',)


class Match(models.Model):
    match_id = models.AutoField(primary_key=True)
    match_competition = models.ForeignKey(CompetitionProfile, on_delete=models.CASCADE)
    match_home_team = models.ForeignKey(TeamProfile, related_name='home_team', on_delete=models.CASCADE)
    match_away_team = models.ForeignKey(TeamProfile, related_name='away_team', on_delete=models.CASCADE)
    match_date = models.DateTimeField()
    match_location = models.ForeignKey(GroundProfile, on_delete=models.CASCADE)
    STATUS = (
        ('Expected', 'Expected'),
        ('Scheduled', 'Scheduled'),
        ('Finished', 'Finished'),
    )
    status = models.CharField(max_length=255, choices=STATUS, null=True)

    def __str__(self):
        return '%s  -  %s ( %s ): %s' % (
            self.match_home_team,
            self.match_away_team,
            self.match_competition,
            self.status,
        )

class Result(models.Model):
    match_result = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_goals = models.PositiveSmallIntegerField()
    away_goals = models.PositiveSmallIntegerField()

    def __str__(self):
        return '%s  %s - %s  %s' % (
            self.match_result.match_home_team,
            self.home_goals,
            self.away_goals,
            self.match_result.match_away_team,
        )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    description = models.CharField(max_length = 250, default = '')
    user_image = models.URLField(null=True, max_length=2000, default = 'https://cdn0.iconfinder.com/data/icons/typicons-2/24/user-256.png')
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




class Comment(models.Model):
    post = models.ForeignKey(GroundProfile, related_name='comments')
    author = models.ForeignKey(User, on_delete = models.PROTECT)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.body
