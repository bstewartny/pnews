#from celery import task
#from celery.task.base import periodic_task
from django.utils.timezone import timedelta
from django.db.models import Q
from portal.tagger import Tagger
from portal.models import *
import time
import datetime
import urllib3
import nltk
import pytz
import portal.tagger
import portal.nlpextractor
import feedparser
from portal.cleaner import clean_text
from . import feeddefs

def dedup():
    c=0
    for d in Document.objects.all():
        c=c+1
        if c % 1000 == 0:
            print('processed '+str(c)+' docs...')
        delete_duplicates(d)

def delete_duplicates(doc):
    Document.objects.filter(feed=doc.feed).filter(title__iexact=doc.title).exclude(id=doc.id).delete()
    Document.objects.filter(title__iexact=doc.title).filter(url=doc.url).exclude(id=doc.id).delete()

def is_duplicate(doc):
    # dup if same feed, same headline
    if Document.objects.filter(feed=doc.feed).filter(title__iexact=doc.title).exclude(id=doc.id).exists():
        return True
    
    # dup if same title, same link (but different feed)
    if Document.objects.filter(title__iexact=doc.title).filter(url=doc.url).exclude(id=doc.id).exists():
        return True
    
    return False

#@task()
def process_doc(doc):

    text=doc.title

    if text is None:
        return
    
    if doc.body is not None:
        text=text+' '+doc.body
    else:
        doc.body=''

    if is_duplicate(doc):
        return

    # save doc
    doc.save()
    
    need_save=False
    # get named entities using NLP
    nlp_entities=portal.nlpextractor.extract_entities(text)
    
    # see if no such entity or pattern already exists, then add it as a disabled new entity
    for nlp_entity in nlp_entities:
        x=(Entity.objects.filter(name__iexact=nlp_entity) | Entity.objects.filter(pattern__pattern__iexact=nlp_entity))
        if len(x)==0:
            print('adding new NLP entity: '+nlp_entity)
            e=Entity(name=nlp_entity)
            e.enabled=False
            e.save()
            p=Pattern(pattern=nlp_entity)
            p.entity=e
            p.save()
            # and attach to this document
            doc.entities.add(e)
            need_save=True

    # get entities using database models
    entities=Tagger.extract_entities(text)

    doc_entity_names=set()
    if entities is not None:
        if len(entities)>0:
            print('found '+str(len(entities)) +' matching entities for document')
            print(str([entity.name for entity in entities]))
            for entity in entities:
                doc.entities.add(entity)
                if entity.parent is not None:
                    doc.entities.add(entity.parent)
                    doc_entity_names.add(entity.parent.name)
                doc_entity_names.add(entity.name)
                need_save=True

    # add entities from feed source
    for e in doc.feed.entities.all():
        # make sure we dont add entities doc already has
        if not e.name in doc_entity_names:
            doc.entities.add(e)
            doc_entity_names.add(e.name)
            need_save=True
        if e.parent is not None:
            if not e.parent.name in doc_entity_names:
                doc.entities.add(e.parent)
                doc_entity_names.add(e.parent.name)
                need_save=True
    
    if need_save:
        doc.save()


def get_attribute(item,names):
  for name in names:
    if name in item:
      return item[name]
  return None


#@task()
def process_feed(feed):
    print('process_feed: '+feed.name)
    # get all items in feed and add as seperate tasks
    rss=feedparser.parse(feed.url)
    for item in rss['items']:
        title=item['title']
        body=clean_text(get_attribute(item,['summary','description']))
        url=item['link']
        doc=Document(title=title,url=url,body=body,feed=feed)
        #TODO: get pub_date from rss item
        # doc.pub_date=''
        #try:
        process_doc(doc)
	#except:
	#	print 'Failed to process doc...'
    	#	continue


#@task()
def process_entity(id):
    e=Entity.objects.get(id=id)
    Tagger.process_entity(e)


#@task()
def process_feeds():
    print('process_feeds')
    for feed in Feed.objects.all():
        process_feed(feed)


#@periodic_task(run_every=timedelta(seconds=5))

#@task()
def process_feeds_periodic():
    print('process_feeds_periodic')
    process_feeds()


def get_or_create_entity(name):
    e=Entity.objects.filter(name=name).first()
    if not e:
        e=Entity(name=name,enabled=True)
        e.save()
    return e


def load_feeds():
    right_wing=get_or_create_entity('Right Wing')
    left_wing=get_or_create_entity('Left Wing')
    for feed in feeddefs.feeds:
        f=Feed(name=feed['feed'],url=feed['rss'])
        f.save()
        wing=feed.get('wing')
        if wing:
            if wing=='right':
                f.entities.add(right_wing)
                f.save()
                
            if wing=='left':
                f.entities.add(left_wing)
                f.save()

