from celery import task
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
import feeddefs

@task()
def process_doc(doc):
    print 'process_doc: '+doc.title

    text=doc.title

    if text is None:
        return
    
    if doc.body is not None:
        text=text+' '+doc.body
    else:
        doc.body=''

    # save doc
    doc.save()
    
    # get named entities using NLP
    nlp_entities=portal.nlpextractor.extract_entities(text)

    # see if no such entity or pattern already exists, then add it as a disabled new entity
    for nlp_entity in nlp_entities:
        x=(Entity.objects.filter(name__iexact=nlp_entity) | Entity.objects.filter(pattern__pattern__iexact=nlp_entity))
        if len(x)==0:
            print 'adding new entity: '+nlp_entity
            e=Entity(name=nlp_entity)
            e.enabled=False
            e.save()
            p=Pattern(pattern=nlp_entity)
            p.entity=e
            p.save()
            # and attach to this document
            doc.entities.add(e)

    # get entities using database models
    entities=portal.tagger.extract_entities(text)

    for entity in entities:
        doc.entities.add(entity)

    doc.save()

def get_attribute(item,names):
  for name in names:
    if name in item:
      return item[name]
  return None

@task()
def process_feed(feed):
    print 'process_feed: '+feed.name
    # get all items in feed and add as seperate tasks
    rss=feedparser.parse(feed.url)
    for item in rss['items']:
        title=item['title']
        body=clean_text(get_attribute(item,['summary','description']))
        url=item['link']
        doc=Document(title=title,url=url,body=body,feed=feed)
        #TODO: get pub_date from rss item
        # doc.pub_date=''
        process_doc(doc)


@task()
def process_feeds():
    print 'process_feeds'
    for feed in Feed.objects.all():
        process_feed(feed)

def load_feeds():
    for feed in feeddefs.feeds:
        f=Feed(name=feed['feed'],url=feed['rss'])
        f.save()

