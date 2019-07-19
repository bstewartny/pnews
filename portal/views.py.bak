from django.http import HttpResponse
from portal.models import *
from portal.index import Index
from django.shortcuts import render
from django.shortcuts import get_object_or_404
import nltk

# Create your views here.

stopwords=nltk.corpus.stopwords.words('english')
stopwords.append('yellow')
stopwords.append('span')


def get_entity_list(request):
    # get from request URL (find entity slugs in path)
    entities=[]
    for slug in [s for s in request.path.split('/') if len(s)>0]:
        entity=get_object_or_404(Entity,slug=slug)
        entities.append(entity)
    return entities

def detail(request,entity_id):
    return HttpResponse('entity %s' % entity_id)

def topics(request):
    # show results grouped by entity/topic, a result set for each one...
    # first get top N entities for the text search
    # for each entity do another sub-query
    
    text_query=request.REQUEST.get('q')
    if text_query is not None:
        if len(text_query)==0:
            text_query=None
    entity_list=[] 
    results=Index.topics(text_query,page_size=5,num_topics=12)
     
    return render(request,'topics.html',{'topics':results}) 

def sources(request):
    # show results grouped by entity/topic, a result set for each one...
    # first get top N entities for the text search
    # for each entity do another sub-query
    results={}
    return render(request,'sources.html',results) 


def get_breadcrumbs(entity_list,query):
    breadcrumbs=[]
    link=''
    if entity_list is not None:
        for entity in entity_list:
            link=link+'/'+entity.slug
            breadcrumbs.append({'name':entity.name,'link':link,'active':False})
    if query is not None:
        if len(query)>0:
            if query!='*':
                link=link+'?q='+query # TODO: encode
                breadcrumbs.append({'name':'"'+query+'"','link':link,'active':False})
    if len(breadcrumbs)>0:
        breadcrumbs[-1]['active']=True
    return breadcrumbs

def index(request):

    text_query=request.REQUEST.get('q')
    if text_query is not None:
        if len(text_query)==0:
            text_query=None

    print 'get entity list'
    entity_list=get_entity_list(request)
    if text_query is None and len(entity_list)==0:
        text_query='*'

    page_number=int(request.REQUEST.get('p',1))
    page_size=20
    facet_max=25
    

    print 'get results'
    results=Index.search(text_query,entity_list,page_number=page_number,facet_max=facet_max,highlight=True,highlight_inline=True,start_tag="<span style='background:yellow'>",end_tag='</span>')
    print 'got results'
    for result in results['results']:
        if result.entities.filter(name='LeftWing').exists():
            result.wing='left'
        else:
            if result.entities.filter(name='RightWing').exists():
                result.wing='right'
            else:
                result.wing='none'

    # adjust facet links to be relative to current path
    facetpath=request.path
    if not facetpath.endswith('/'):
        facetpath=facetpath+'/'

    facetquery=''
    if text_query is not None and len(text_query)>0 and text_query!='*':
        facetquery='?q='+text_query #TODO: encode query
        title='"'+text_query+'"'
    else:
        if len(entity_list)>0:
            title=entity_list[-1].name
        else:
            title='Search'

    all_titles=''

    print 'get word cloud'
    for doc in results['results']:
        all_titles=all_titles+' '+doc.title
        
    all_words=nltk.word_tokenize(all_titles.lower())

    # TODO: include patterns from entities, remove noise words
    tagcloud=[{'text':word,'freq':all_words.count(word),'link':request.path+'?q='+word} for word in set(all_words) if not word in stopwords and word.isalpha()]

    results['breadcrumbs']=get_breadcrumbs(entity_list,text_query)
    results['facetpath']=facetpath
    results['facetquery']=facetquery
    results['title']=title
    results['tagcloud']=tagcloud

    print 'render'
    return render(request,'index.html',results) 

