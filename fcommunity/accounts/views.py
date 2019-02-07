# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from accounts.forms import RegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse
from accounts.models import TeamProfile, CompetitionProfile, UserProfile

# Create your views here.



def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/account/login')
    else:
        form = RegistrationForm()
    args = {'form': form}
    return render(request, 'accounts/reg_form.html', args)

@login_required
def profile(request):
    args = {'user': request.user}
    return render(request, 'accounts/profile.html', args)

def team_profile(request, pk):
    team = TeamProfile.objects.get(team_id = pk)
    return render(request, 'accounts/team_profile.html', {"team":team})

def user_profile(request, pk):
    userp = User.objects.get(pk = pk)
    return render(request, 'accounts/user_profile.html', {"user":userp})

def comp_profile(request, pk):
    comp = CompetitionProfile.objects.get(comp_id = pk)
    return render(request, 'accounts/comp_profile.html', {"comp":comp})

def all_teams(request):
    template = loader.get_template('accounts/all_teams.html')
    context = {'teams': TeamProfile.objects.all()}
    return HttpResponse(template.render(context, request))

def all_comps(request):
    template = loader.get_template('accounts/all_comps.html')
    context = {'comps': CompetitionProfile.objects.all()}
    return HttpResponse(template.render(context, request))
