from portal.models import *
import nltk
        
def clusterize():
    # maybe use DBSCAN
    pass


def get_tokens(text):
    # TODO: strip stop words
    return [word for word in nltk.word_tokenize(text.lower()) if word.isalpha()]


def jaccard_distance(a,b):
    """
    A simple distance function (curse of dimensionality applies)
    """
    # tokenize into bag of words
    f1 = set(get_tokens(a)[:100])
    f2 = set(get_tokens(b)[:100])
   
    sim = 1.0*len(f1.intersection(f2))/len(f1.union(f2))

    return 1.0 - sim


def kmeans(k=10,distance_function=jaccard_distance,threshold=0.80,items):
    centroids=random.sample(item,k)
    items=list(set(items) - set(centroids))
    last_matches=None
    for t in range(50):
        best_matches=[[] for c in centroids]
        min_distance=1.0

        for item in items:
            best_center=0
            min_distance=1.0
            minima=-1
            for centroid in centroids:
                minima+=1
                distance=distance_function(item,centroid)
                if distance <= min_distance:
                    best_center=minima
                    min_distance=distance
            if min_distance <=threshold:
                best_matches[best_center].append(item)

        if best_matches==last_matches:
            break
        last_matches=best_matches





