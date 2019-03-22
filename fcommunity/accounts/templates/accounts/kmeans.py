# %matplotlib inline
# import matplotlib.pyplot as plt
# import seaborn as sns; sns.set()  # for plot styling
# import numpy as np
# from sklearn.datasets.samples_generator import make_blobs
# X, y_true = make_blobs(n_samples=300, centers=4,
#                        cluster_std=0.60, random_state=0)
# plt.scatter(X[:, 0], X[:, 1], s=50);



# https://jakevdp.github.io/PythonDataScienceHandbook/05.11-k-means.html


from sklearn.cluster import KMeans
import numpy as np
from django.contrib.auth.models import User
from accounts.models import TeamProfile, GroundProfile, UserProfile
from geopy.distance import vincenty


def kmeansUsers():
    leaveList = []
    for user in User.objects.all():
        if user.userprofile.wantsToLeave:
            leaveList.append(user)
    return leaveList
