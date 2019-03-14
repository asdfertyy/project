# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import RegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse
from .forms import CommentForm, LocationForm
from accounts.models import TeamProfile, CompetitionProfile, GroundProfile, Match, Result, UserProfile

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

def team_history(request, pk):
    team = TeamProfile.objects.get(team_id = pk)
    return render(request, 'accounts/history.html', {"team":team})

def user_profile(request, pk):
    userp = User.objects.get(pk = pk)
    return render(request, 'accounts/user_profile.html', {"user":userp})

def comp_profile(request, pk):
    comp = CompetitionProfile.objects.get(comp_id = pk)
    return render(request, 'accounts/comp_profile.html', {"comp":comp})

def ground_profile(request, pk):
    ground = GroundProfile.objects.get(ground_id = pk)
    return render(request, 'accounts/ground_profile.html', {"ground":ground})

def all_teams(request):
    template = loader.get_template('accounts/all_teams.html')
    context = {'teams': TeamProfile.objects.all()}
    return HttpResponse(template.render(context, request))

def all_comps(request):
    template = loader.get_template('accounts/all_comps.html')
    context = {'comps': CompetitionProfile.objects.all()}
    return HttpResponse(template.render(context, request))

def all_grounds(request):
    template = loader.get_template('accounts/all_grounds.html')
    context = {'grounds': GroundProfile.objects.all()}
    return HttpResponse(template.render(context, request))

def all_usrs(request):
    template = loader.get_template('accounts/all_usrs.html')
    context = {'usrs': User.objects.all()}
    return HttpResponse(template.render(context, request))

@login_required
def add_comment_to_ground(request, pk):
    ground = GroundProfile.objects.get(ground_id = pk)
    #get_object_or_404(GroundProfile, ground_id=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = ground
            comment.author = request.user
            comment.save()
            return redirect('ground_profile', pk = ground.ground_id)
    else:
        form = CommentForm()
    return render(request, 'accounts/add_comment_to_ground.html', {'form': form})

@login_required
def new_ground(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            GroundProfile = form.save(commit=False)
            GroundProfile.save()
            return redirect('/account/profile')
    else:
        form = LocationForm()
    return render(request, 'accounts/new_ground.html', {'form': form})

