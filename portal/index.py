from django.db import models
from django.db.models import Count
from random import randrange
from portal.highlighter import Highlighter
from portal.models import *

class Index:

    @staticmethod
    def get_field_facets(results_filter,field_name,field_objects,top=10):
        facets=results_filter.filter(**{'{0}__isnull'.format(field_name):False}).values(field_name).annotate(freq=Count(field_name)).order_by('-freq')[:top]
        for facet in facets:
            e=field_objects.get(id=facet[field_name])
            facet['name']=e.name
        return facets

    @staticmethod    
    def get_results_facets(results,top=10):
        if top>0 and results is not None:
            ids=results.values_list('id',flat=True)
            print "len(ids)="+str(len(ids))
            print str(ids)
            results_filter=Document.objects.filter(id__in=ids)
    
            entity_facets=Index.get_field_facets(results_filter,'entities',Entity.objects,top)
            feed_facets=Index.get_field_facets(results_filter,'feed',Feed.objects,top)

            return {'entities':entity_facets,'feeds':feed_facets}
        else:
            return {}

    @staticmethod    
    def get_doc_highlights(doc,words,start_tag='<b>',end_tag='</b>'):
        if type(doc) is int:
            doc=Document.objects.get(id=doc)
        title=' '+doc.title+' '
        body=' '+doc.body+' '
        for word in words:
            title=Highlighter.highlight_word(title,word,start_tag,end_tag)
            body=Highlighter.highlight_word(body,word,start_tag,end_tag)
    
        title=title.strip()
        body=body.strip()
        return {'title':title,'body':body}

    @staticmethod    
    def get_result_highlights(docs,words,start_tag='<b>',end_tag='</b>'):
        h={}
        if len(words)>0:
            for doc in docs:
                h[doc.id]=Index.get_doc_highlights(doc,words,start_tag,end_tag)
        return h


    @staticmethod    
    def search(text,entities=[],page_size=10,page_number=1,sort='-pub_date',facet_max=0,highlight=False,start_tag='<b>',end_tag='</b>'):
        
        if page_number<1: 
            page_number=1
            print 'feed facets query:'
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
            facets=Index.get_results_facets(results,facet_max)
            docs=results.order_by(sort)[start:end]
            highlights={}
            if docs.count()>0:
                if highlight:
                    words=Index.get_highlight_words(text,entities)
                    if len(words)>0:
                        highlights=Index.get_result_highlights(docs,words,start_tag,end_tag)
            
            return {'query':text,'results':docs,'facets':facets,'highlights':highlights}
        else:
            return {'query':text,'results':[],'facets':{},'highlights':{}}
