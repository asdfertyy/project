from django import forms
from django.contrib.auth.models import User
from .models import Comment, Chat, Result, GroundProfile, UserProfile, TeamProfile, CompetitionProfile, Match
import urllib, urllib2, simplejson
import json
from decimal import Decimal
from django.utils.encoding import smart_str
# from django.contrib.auth.models import Comment
from django_google_maps.widgets import GoogleMapsAddressWidget
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )


        def save(self, commit = True):
            user = super(RegistrationForm, self).save(commit = False)
            user.first_name = cleaned_data('first_name')
            user.last_name = cleaned_data('last_name')
            user.email = cleaned_data('email')
            # user.address = cleaned_data('address')
            # user.birthday = cleaned_data('birthday')

            if commit:
                user.save()

            return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ('body',)

class LocationForm(forms.ModelForm):
    class Meta:
        model = GroundProfile
        exclude = ('ground_address', )
        widgets = {'ground_latitude': forms.HiddenInput(), 'ground_longitude': forms.HiddenInput()}

        # def save(self):
        #     if not self.ground_latitude or not self.ground_longitude:
        #         self.ground_latitude, self.ground_longitude = self.get_lat_lng(self.ground_address)
        #
        #     super(GroundProfile, self).save()
        #
        # def get_lat_lng(ground_address):
        #
        #     address = urllib.parse.quote_plus(ground_address)
        #     maps_api_url = "?".join(["http://maps.googleapis.com/maps/api/geocode/json",urllib.parse.urlencode({"address" = address, "sensor" = False})])
        #     response = urllib.urlopen(maps_api_url)
        #     data = json.loads(response.read().decode('utf8'))
        #
        #     if data['status'] == 'OK':
        #         lat = data['results'][0]['geometry']['location']['lat']
        #         lng = data['results'][0]['geometry']['location']['lng']
        #         return Decimal(lat), Decimal(lng)

class EditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'date_joined', 'teams', 'wantsToLeave', 'temp_team',)
        widgets = {'user_latitude': forms.HiddenInput(), 'user_longitude': forms.HiddenInput()}

class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = TeamProfile
        exclude = ('team_date_joined', 'comps')

class CompCreationForm(forms.ModelForm):
    class Meta:
        model = CompetitionProfile
        exclude = ('match_result',)

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        exclude = ('match_result',)

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        exclude = ('match_competition', 'match_home_team', 'match_away_team', 'stage', 'status')
