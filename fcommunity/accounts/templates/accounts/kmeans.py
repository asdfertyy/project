import numpy as np
from sklearn.cluster import KMeans

# noOfSearchers -> number of people that are looking for a new team
# searchers[][] -> longitudes and latitudes of searchers
clustersToDo = (noOfSearchers / 11) + 1
kmeans = KMeans(n_clusters = clustersToDo)
kmeans.fit(searchers)
y_kmeans = kmeans.predict(searchers)



# https://jakevdp.github.io/PythonDataScienceHandbook/05.11-k-means.html