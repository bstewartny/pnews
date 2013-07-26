from portal.models import *
import nltk
import random

nltk_stopwords=nltk.corpus.stopwords.words('english')

def get_tokens(text):
    # TODO: strip stop words
    return [word for word in nltk.word_tokenize(text.lower()) if word.isalpha() and not word in nltk_stopwords]


def jaccard_distance(a,b):
    """
    A simple distance function (curse of dimensionality applies)
    """
    # tokenize into bag of words
    # TODO: dont re-create text content - need to cache title+body
    f1 = a[1]
    f2 = b[1]
   
    sim = 1.0*len(f1.intersection(f2))/len(f1.union(f2))

    return 1.0 - sim


def create_features(item,max=100):
    return (item.id,set(get_tokens(item.content())[:max]))

def create_features_array(items,max=100):
    return [create_features(item,max) for item in items]

def print_clusters(c):
    for a in c:
        for d in a:
            doc=Document.objects.get(id=d[0])
            print doc.title
        print '----'

def compute_centroid(centroid,cluster):
    # find average somehow...
    h={}
    for w in centroid:
        h[w]=1+h.setdefault(w,0)

    for d in cluster:
        for w in d:
            h[w]=1+h.setdefault(w,0)
    
    t=sorted(h.iteritems(),key=operator.itemgetter(1),reverse=True)[:100]
    
    return set([x[0] for x in t])





def kmeans(items,k=20,distance_function=jaccard_distance,threshold=0.80):
    
    items_features=create_features_array(items)
    
    centroids=random.sample(items_features,k)
    
    items_features=[i for i in items_features if i[0] not in [j[0] for j in centroids]]
    
    last_matches=None
    count=0
    
    for t in range(100):
        best_matches=[[] for c in centroids]
        min_distance=1.0

        for item in items_features:
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
            print 'we reached stable clusters, break from loop'
            break

        # recompute centroids
        for i in range(len(centroids)):
            centroid=centroids[i]
            centroid_cluster=best_matches[i]
            new_centroid=compute_centroid(centroid,centroid_cluster)
            centriods[i]=new_centroid

        count=count+1
        last_matches=best_matches
    
    print 'iterations: '+str(count)
    return last_matches





