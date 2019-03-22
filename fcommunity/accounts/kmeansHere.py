from sklearn.cluster import KMeans
import numpy as np
from django.contrib.auth.models import User

from accounts.models import TeamProfile, GroundProfile, UserProfile
from accounts.views import tempTeamCount, count, teamMaxSize, teamMinSize, leaveList
from geopy.distance import vincenty
from collections import Counter, defaultdict
# leaveList = []                          # Users that want to leave
# latLonList = []                         # List with lat and lng of those users
# teamMinSize = 5
# teamMaxSize = 15
# count = 1
for user in User.objects.all():
    if user.userprofile.wantsToLeave:
        leaveList.append(user)
finalIndices = [0] * len(leaveList)
for user in leaveList:
    latLonList.append([user.userprofile.user_latitude, user.userprofile.user_longitude])
givenList = np.array(latLonList)

def shoudAlgoStart():
    return (len(leaveList) > 100)

def kmeansUsers(givenList, prevIndexList):
    global count, teamMinSize, teamMaxSize, finalIndices
    clusterCount = len(givenList) / 10 + 1
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
    return finalIndices, count - 1

def checkIfValid(finalIndices, clusterCount):
    minDist = 100
    minPointIndex = ''
    clusterDiscardList = []
    for cluster in range(1, clusterCount):          # make sure the clusters generated are valid (by distance)
        clusterList = []
        indexList = []

        for index in finalIndices:
            if finalIndices[index] == cluster:
                clusterList.append(latLonList[index])
                indexList.append(index)
        for index in range (0, len(clusterList) - 2):
            for index2 in range (index + 1, len(clusterList) - 1):
                if vincenty((clusterList[index].x, clusterList[index].y), (clusterList[index2].x, clusterList[index2].y)).kilometers > 30:
                    for i in indexList:
                        finalIndices[i] = 0
                        clusterDiscardList.append(cluster)
                    break
    for index in finalIndices:                      # try to assign non-assigned users to temporary teams
        if finalIndices[index] == 0:
            for j in latLonList:
                if finalIndices[j] != 0:
                    if vincenty((latLonList[index].x, latLonList[index].y),(latLonList[j].x, latLonList[j].y)).kilometers < minDist:
                        minDist = vincenty((latLonList[index].x, latLonList[index].y),(latLonList[j].x, latLonList[j].y)).kilometers
                        minPointIndex = j
        if minDist < 15:
            finalIndices[index] = finalIndices[minPointIndex]
    return finalIndices



def updateDb(finalIndices, clusterCount, clusterDiscardList):
    for cluster in range(1, clusterCount):
        if cluster not in clusterDiscardList:
            currTempTeam = TemporaryTeamProfile.objects.create(name=("Temporary Team %s" % tempTeamCount))
            tempTeamCount += 1
            for i in finalIndices:
                if finalIndices[index] == cluster:
                    userToAdd = leaveList[i]
                    userToAdd.userprofile.update(tempTeam = currTempTeam)