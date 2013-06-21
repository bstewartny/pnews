from django.http import HttpResponse
from portal.models import *
from portal.index import Index
from django.shortcuts import render

# Create your views here.

def get_entity_list(request):
    e=request.REQUEST.get('e')
    if e is not None and len(e)>0:
        return [int(i) for i in e.split(',')]
    else:
        return []


def detail(request,entity_id):
    return HttpResponse('entity %s' % entity_id)

def topics(request):
    # show results grouped by entity/topic, a result set for each one...
    # first get top N entities for the text search
    # for each entity do another sub-query
    pass

def sources(request):
    # show results grouped by entity/topic, a result set for each one...
    # first get top N entities for the text search
    # for each entity do another sub-query
    pass


def index(request):

    text_query=request.REQUEST.get('q')
    entity_list=get_entity_list(request)
    if text_query is None and len(entity_list)==0:
        text_query='*'

    page_number=int(request.REQUEST.get('p',1))
    page_size=20
    facet_max=25
    
    results=Index.search(text_query,entity_list,page_number=page_number,facet_max=facet_max)
    docs=results['results']
    facets=results['facets']

    return render(request,'index.html',results) 

