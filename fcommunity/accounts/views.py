# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import RegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse
from .forms import MatchForm, ResultForm, ChatForm, CommentForm, LocationForm, EditForm, TeamCreationForm, CompCreationForm
from accounts.models import TeamProfile, TempTeamProfile, CompetitionProfile, GroundProfile, Match, Result, UserProfile
from geopy.distance import vincenty
from sklearn.cluster import KMeans
import numpy as np
import random
# from . import kmeansHere
from collections import Counter, defaultdict
import math
# Create your views here.
tempTeamCount = 1
teamMinSize = 2
teamMaxSize = 2
count = 1
leaveList = []
finalIndices = []
latLonList = []  # List with lat and lng of those users

def increment():
    global tempTeamCount
    tempTeamCount += 1

def cleanTeams():
    for temp in TempTeamProfile.objects.all():
        if temp.userprofile_set.count() == 0:
            temp.delete()
    for team in TeamProfile.objects.all():
        if team.userprofile_set.count() == 0:
            team.delete()

def startCompetition(comp):
    teamsList = comp.teamprofile_set.all()
    comp.has_matches = True
    comp.save()
    # teamsList = random.shuffle(list(teamsList))
    if comp.comp_type == 'Cup':
        for i in range(0, len(teamsList) - 1, 2):
            newMatch = Match.objects.create(match_competition=comp, match_home_team=teamsList[i],match_away_team=teamsList[i+1], status='Expected', stage = 1)
    else:
        for i in range(0, len(teamsList) - 1):
            for j in range(0, len(teamsList) - 1):
                if i != j:
                    newMatch = Match.objects.create(match_competition = comp, match_home_team = teamsList[i], match_away_team = teamsList[j], status = 'Expected')

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
    global leaveList, finalIndices, latLonList, count
    if request.GET.get('leaveTeamBtn'):
        user = request.user
        user.userprofile.teams = None
        user.userprofile.save()
        return redirect('profile')
    if request.GET.get('joinRecTeamBtn'):
        user = request.user
        newTeam = TeamProfile.objects.create(team_name = '%s' % user.userprofile.temp_team)
        currTemp = user.userprofile.temp_team
        for userprofiles in currTemp.userprofile_set.all():
            userprofiles.teams = None
            userprofiles.teams = newTeam
            userprofiles.temp_team = None
            userprofiles.wantsToLeave = False
            userprofiles.save()
        cleanTeams()
        return redirect('profile')
    if request.GET.get('thinkOfLeavingBtn'):
        user = request.user
        user.userprofile.wantsToLeave = not user.userprofile.wantsToLeave
        user.userprofile.save()
        leaveList = []
        for user1 in User.objects.all():
            if user1.userprofile.wantsToLeave:
                leaveList.append(user1)
        if len(leaveList) > 4:
            finalIndices = [0] * len(leaveList)
            for user3 in leaveList:
                latLonList.append([user3.userprofile.user_latitude, user3.userprofile.user_longitude])
            givenList = np.array(latLonList)
            finalIndices, clusterCount = kmeansUsers(givenList, '')
            finalIndices, clusterCount, clusterDiscardList = checkIfValid(finalIndices, clusterCount)
            updateDb(finalIndices, clusterCount, clusterDiscardList)
            leaveList = []
            latLonList = []
            givenList = []
            count = 1
        return redirect('profile')
    args = {'user': request.user, 'teams': TeamProfile.objects.all()}
    return render(request, 'accounts/profile.html', args)


def kmeansUsers(givenList, prevIndexList):
    global count, teamMinSize, teamMaxSize
    clusterCount = len(givenList) / 3 + 1
    kmeans = KMeans(n_clusters=(clusterCount))
    kmeans.fit(givenList)
    clusters_indices = defaultdict(list)
    for i, j in enumerate(kmeans.labels_):
        clusters_indices[j].append(i)
    for clusterNumber in range(0, clusterCount):
        clusterPointCount = Counter(kmeans.labels_)[clusterNumber]
        if clusterPointCount < teamMinSize:
            pass
        elif clusterPointCount <= teamMaxSize:
            if prevIndexList:
                for index in clusters_indices[clusterNumber]:
                    finalIndices[prevIndexList[index]] = count
            else:
                for index in clusters_indices[clusterNumber]:
                    finalIndices[index] = count
            count += 1
        else:
            newList = []
            for index in clusters_indices[clusterNumber]:
                currPoint = (givenList[index][0], givenList[index][1])
                newList.append(currPoint)
            arrayList = np.array(newList)
            if prevIndexList:
                valueList = []
                for index in clusters_indices[clusterNumber]:
                    valueList.append(prevIndexList[index])
                kmeansUsers(arrayList, valueList)
            else:
                kmeansUsers(arrayList, clusters_indices[clusterNumber])
    return finalIndices, int(count - 1)

def checkIfValid(finalIndices, clusterCount):
    minPointIndex = ''
    clusterDiscardList = []
    global latLonList
    for cluster in range(1, (clusterCount + 1)):          # make sure the clusters generated are valid (by distance)
        clusterList = []
        indexList = []

        for index, value in enumerate(finalIndices):
            if value == cluster:
                clusterList.append(latLonList[index])
                indexList.append(index)
        for index in range(0, len(clusterList) - 1):
            for index2 in range(index + 1, len(clusterList)):
                if vincenty((clusterList[index][0], clusterList[index][1]), (clusterList[index2][0], clusterList[index2][1])).kilometers > 30:
                    for i, val in enumerate(indexList):
                        finalIndices[i] = 0
                        clusterDiscardList.append(cluster)
                    break
    for index, value in enumerate(finalIndices):                      # try to assign non-assigned users to temporary teams
        minDist = 100000
        if value == 0:
            for idx, value in enumerate(latLonList):
                if finalIndices[idx] != 0:
                    if vincenty((latLonList[index][0], latLonList[index][1]), (latLonList[idx][0], latLonList[idx][1])).kilometers < minDist:
                        minDist = vincenty((latLonList[index][0], latLonList[index][1]), (latLonList[idx][0], latLonList[idx][1])).kilometers
                        minPointIndex = idx
        if minDist < 15 and finalIndices.count(finalIndices[minPointIndex]) <=5:
            finalIndices[index] = finalIndices[minPointIndex]
    clusterList = []
    return finalIndices, clusterCount, clusterDiscardList



def updateDb(finalIndices, clusterCount, clusterDiscardList):
    global tempTeamCount, leaveList
    for cluster in range(1, (clusterCount + 1)):
        if cluster not in clusterDiscardList:
            currTempTeam = TempTeamProfile.objects.create(tempTeam_name=("Temporary Team %s" % tempTeamCount))
            increment()
            for i, value in enumerate(finalIndices):
                if value == cluster:
                    userToAdd = leaveList[i]
                    currTempTeam.userprofile_set.add(userToAdd.userprofile)


def team_profile(request, pk):
    team = TeamProfile.objects.get(team_id = pk)
    if request.GET.get('joinTeamBtn'):
        user = request.user
        user.userprofile.teams = team
        user.userprofile.save()
        return redirect('profile')
    return render(request, 'accounts/team_profile.html', {"team":team})

def team_history(request, pk):
    team = TeamProfile.objects.get(team_id = pk)
    return render(request, 'accounts/history.html', {"team":team})

def user_profile(request, pk):
    userp = User.objects.get(pk = pk)
    return render(request, 'accounts/user_profile.html', {"user":userp})

def comp_profile(request, pk):
    comp = CompetitionProfile.objects.get(comp_id = pk)
    if request.GET.get('joinCompBtn'):
        user = request.user
        user.userprofile.teams.comps.add(comp)
        user.userprofile.teams.save()
        if comp.teamprofile_set.all().count() == comp.comp_teamNumber:
            startCompetition(comp)
        return redirect('comp_profile', pk = comp.comp_id)
    user = request.user
    return render(request, 'accounts/comp_profile.html', {"comp":comp, 'user': user, 'teams': TeamProfile.objects.all()})

def view_comp_matches(request, pk):
    comp = CompetitionProfile.objects.get(comp_id = pk)
    #get_object_or_404(GroundProfile, ground_id=pk)
    return render(request, 'accounts/view_comp_matches.html', {'comp': comp, 'matches': Match.objects.all()})
def match_profile(request, pk):
    match = Match.objects.get(match_id = pk)
    return render(request, 'accounts/match_profile.html', {'match': match})

def ground_profile(request, pk):
    ground = GroundProfile.objects.get(ground_id = pk)
    return render(request, 'accounts/ground_profile.html', {"ground": ground})

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

def all_user_locs(request):
    template = loader.get_template('accounts/all_user_locs.html')
    context = {'users': User.objects.all()}
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
            return redirect('ground_profile', pk=ground.ground_id)
    else:
        form = CommentForm()
    return render(request, 'accounts/add_comment_to_ground.html', {'form': form})

@login_required
def add_message_to_match(request, pk):
    match = Match.objects.get(match_id = pk)
    #get_object_or_404(GroundProfile, ground_id=pk)
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.post = match
            chat.author = request.user
            chat.save()
            return redirect('match_profile', pk=match.match_id)
    else:
        form = ChatForm()
    return render(request, 'accounts/add_message_to_match.html', {'form': form})

# @login_required
# def add_location(request, pk):
#     ground = GroundProfile.objects.get(ground_id = pk)
#     #get_object_or_404(GroundProfile, ground_id=pk)
#     if request.method == "POST":
#         form = LocForm(request.POST or None, instance = ground)
#         if form.is_valid():
#             ground = GroundProfile.objects.get(ground_id=pk)
#             form.save()
#             # ground.save()
#             return redirect('ground_profile', pk=ground.ground_id)
#     else:
#         form = LocForm()
#     return render(request, 'accounts/add_location.html', {'form': form})


@login_required
def new_ground(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            GroundProfile = form.save(commit=False)
            GroundProfile.save()
            return redirect('ground_profile', pk=GroundProfile.ground_id)
    else:
        form = LocationForm()
    return render(request, 'accounts/new_ground.html', {'form': form})


@login_required
def create_team(request):
    if request.method == "POST":
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            TeamProfile = form.save(commit=False)
            TeamProfile.save()
            user = request.user
            user.userprofile.teams = None
            user.userprofile.teams = TeamProfile
            user.userprofile.save()
            cleanTeams()
            return redirect('team_profile', pk=TeamProfile.team_id)
    else:
        form = TeamCreationForm()
    return render(request, 'accounts/create_team.html', {'form': form, 'grounds': GroundProfile.objects.all()})

@login_required
def create_comp(request):
    if request.method == "POST":
        form = CompCreationForm(request.POST)
        if form.is_valid():
            CompetitionProfile = form.save(commit=False)
            CompetitionProfile.save()
            user = request.user
            user.userprofile.teams.comps.add(CompetitionProfile)
            user.userprofile.teams.save()
            cleanTeams()
            return redirect('comp_profile', pk=CompetitionProfile.comp_id)
    else:
        form = CompCreationForm()
    return render(request, 'accounts/create_comp.html', {'form': form})

def getKey(item):
    return item[1]

@login_required
def join_team(request):
    # args = {'user': request.user}
    template = loader.get_template('accounts/join_team.html')
    finalList = []
    userPoint = (request.user.userprofile.user_latitude, request.user.userprofile.user_longitude)
    teamList = TeamProfile.objects.all()
    for team in teamList:
        if(team.team_address is not None):
            teamPoint = (team.team_address.ground_latitude, team.team_address.ground_longitude)
            teamDist = vincenty(userPoint, teamPoint).kilometers
            if teamDist < 15:
                finalList.append([team, teamDist])
    finalList = sorted(finalList, key=getKey)
    context = {'teams': TeamProfile.objects.all(), 'user': request.user, 'nearby_list': finalList}
    return HttpResponse(template.render(context, request))

@login_required
def edit_profile(request):
    user = request.user.userprofile
    #get_object_or_404(GroundProfile, ground_id=pk)
    if request.method == "POST":
        form = EditForm(request.POST or None, instance = user)
        if form.is_valid():
            user = request.user.userprofile
            form.save()
            return redirect('profile')
    else:
        form = EditForm()
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def submit_result(request, pk):
    if request.method == "POST":
        form = ResultForm(request.POST)
        if form.is_valid():
            Result = form.save(commit=False)
            match = Match.objects.get(match_id=pk)
            Result.match_result = match
            Result.save()
            match.status = 'Finished'
            match.save()
            return redirect('match_profile', pk=match.match_id)
    else:
        form = ResultForm()
    return render(request, 'accounts/submit_result.html', {'form': form})

@login_required
def edit_match(request, pk):
    match = Match.objects.get(match_id=pk)
    #get_object_or_404(GroundProfile, ground_id=pk)
    if request.method == "POST":
        form = MatchForm(request.POST or None, instance = match)
        if form.is_valid():
            match = Match.objects.get(match_id=pk)
            form.save()
            # ground.save()
            return redirect('match_profile', pk=match.match_id)
    else:
        form = MatchForm()
    return render(request, 'accounts/edit_match.html', {'form': form})
