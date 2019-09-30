from django.db import models
from django.db.models import Count
from random import randrange
from portal.highlighter import Highlighter
from portal.models import *
from datetime import timedelta

class Zeitgeist:

    @staticmethod
    def get_zeitgeist_facets():
        days_back=10
        # get todays (most recent) 
        most_recent_date=Document.objects.all().order_by('-modified_date').first().modified_date
        most_recent_date=most_recent_date.date()
        most_recent_docs=Document.objects.filter(modified_date__date=most_recent_date)
        top=5
        entity_facets=Index.get_field_facets(most_recent_docs,'entities',Entity.objects,top)
        
        #for i in range(days_back):
        #    previous_date=most_recent_date - timedelta(days=1+i)
        #    previous_docs=Document.objects.filter(modified_date__date=previous_date)
        #    previous_entity_facets=Index.get_field_facets(previous_docs,'entities',Entity.objects,top)
             
            
        
        
        
        
        
        
        facets= {'entities':entity_facets}
        page_size=5
        sort='-pub_date'

        results=None
        topics=[]
        for facet in facets['entities']:
            name=facet['name']
            slug=facet['slug']
            topics.append({'name':name,'slug':slug,'results':most_recent_docs.filter(entities=facet['entities']).order_by(sort)[:page_size]})
        return topics
         

class Index:

    @staticmethod
    def get_field_facets(results_filter,field_name,field_objects,top=10):
        facets=results_filter.filter(**{'{0}__isnull'.format(field_name):False,'{0}__enabled'.format(field_name):True}).values(field_name).annotate(freq=Count(field_name)).order_by('-freq')[:top]
        for facet in facets:
            e=field_objects.get(id=facet[field_name])
            facet['name']=e.name
            facet['slug']=e.slug
        return facets

    @staticmethod    
    def get_results_facets(results,top=10):
        if top>0 and results is not None:
            ids=results.values_list('id',flat=True)
            results_filter=Document.objects.filter(id__in=ids)
            entity_facets=Index.get_field_facets(results_filter,'entities',Entity.objects,top)
            feed_facets=None #Index.get_field_facets(results_filter,'feed',Feed.objects,top)
            return {'entities':entity_facets,'feeds':feed_facets}
        else:
            return {}

    @staticmethod    
    def get_doc_highlights(doc,patterns,start_tag='<b>',end_tag='</b>'):
        if type(doc) is int:
            doc=Document.objects.get(id=doc)
        title=' '+doc.title+' '
        body=' '+doc.body+' '
        for pattern in patterns:
            title=Highlighter.highlight_re(title,pattern,start_tag,end_tag)
            body=Highlighter.highlight_re(body,pattern,start_tag,end_tag)
    
        title=title.strip()
        body=body.strip()
        return {'title':title,'body':body}

    @staticmethod    
    def get_result_highlights(docs,patterns,start_tag='<b>',end_tag='</b>'):
        h={}
        if len(patterns)>0:
            for doc in docs:
                h[doc.id]=Index.get_doc_highlights(doc,patterns,start_tag,end_tag)
        return h

    @staticmethod
    def topics(text,page_size=10,sort='-pub_date',num_topics=16):
        if page_size<0:
            page_size=0
        if sort is None:
            sort='-pub_date'

        results=None
        if text is None or text=="*":
            text=None
            results=Document.objects.all()
        else:
            results=Document.objects.search(text)
        
        facets=Index.get_results_facets(results,num_topics)
        topics=[]
        for facet in facets['entities']:
            name=facet['name']
            slug=facet['slug']
            print(str(facet))
            topics.append({'name':name,'slug':slug,'results':results.filter(entities=facet['entities']).order_by(sort)[:page_size]})
        return topics


    @staticmethod    
    def search(text,entities=[],page_size=10,page_number=1,sort='-pub_date',facet_max=0,highlight=False,highlight_inline=False,start_tag='<b>',end_tag='</b>'):
        
        if page_number<1: 
            page_number=1
            print('feed facets query:')
        if page_size<0:
            page_size=0
        if sort is None:
            sort='-pub_date'
        if facet_max<0:
            facet_max=0
        
        start=(page_number-1)*page_size
        end=start+page_size
        results=None

        if text:
            if text=='*':
                text=None
                results=Document.objects.all()
            else:
                results=Document.objects.search(text)
            if entities:
                for entity in entities:
                    results=results.filter(entities=entity)
        else:
            if entities:
                results=Document.objects.filter(entities=entities[0])
                if len(entities)>1:
                    for i in range(1,len(entities)):
                        results=results.filter(entities=entities[i])

        if results:
            print('get results facets')
            facets=Index.get_results_facets(results,facet_max)
            print('got facets')
            print('get docs')
            docs=results.order_by(sort)[start:end]
            print('get highlights')
            highlights={}
            if docs.count()>0:
                if highlight:
                    patterns=Highlighter.get_highlight_patterns(text,entities)
                    if len(patterns)>0:
                        highlights=Index.get_result_highlights(docs,patterns,start_tag,end_tag)
                        if highlight_inline:
                            for doc in docs:
                                if doc.id in highlights:
                                    highlight=highlights[doc.id]
                                    doc.title=highlight['title']
                                    doc.body=highlight['body']
                            highlights={}
            if text is None:
                text=''
            return {'query':text,'results':docs,'facets':facets,'highlights':highlights}
        else:
            if text is None:
                text=''
            return {'query':text,'results':[],'facets':{},'highlights':{}}
