from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField
from django.db import models
from portal.highlighter import Highlighter

# Create your models here.
class Entity(models.Model):
    name=models.CharField(max_length=200)
    modified_date=models.DateTimeField(auto_now=True)
    enabled=models.BooleanField(default=True)

    def num_docs(self):
        return Document.objects.filter(entities=self).count()

    def merge(self,others):
        a=[]
        current_patterns=[p.pattern for p in self.pattern_set.all()]
        for other in others:
            a.append(other.name)
            for p in other.pattern_set.all():
                if not p.pattern in current_patterns:
                    if not p.pattern in a:
                        a.append(p.pattern)
        for p in a:
            self.pattern_set.add(Pattern(pattern=p,entity=self))
        self.save()
       
        # update all documents which have other entities to use this entity instead...
        for document in Document.objects.filter(entities__in=others):
            if document.entities.filter(id=self.id).count()==0:
                document.entities.add(self)
                document.save()

        for other in others:
            other.delete()

    def __unicode__(self):
        return self.name


class Feed(models.Model):
    name=models.CharField(max_length=200)
    url=models.CharField(max_length=200)
    entities=models.ManyToManyField(Entity)
   
    def num_docs(self):
        return Document.objects.filter(feed=self).count()
    
    def __unicode__(self):
        return self.name

class Document(models.Model):
    title=models.CharField(max_length=200)
    pub_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    body=models.TextField()
    url=models.CharField(max_length=500)
    entities=models.ManyToManyField(Entity)     
    feed=models.ForeignKey(Feed)

    search_index=VectorField()
    objects=SearchManager(
            fields=('title','body'),
            config='pg_catalog.english',
            search_field='search_index',
            auto_update_search_field=True
            )
   
    def highlighted(self):
        text=self.title+' \n'+self.body
        return Highlighter.highlight_text(text,None,self.entities.all())

    def num_entities(self):
        return self.entities.count()

    def __unicode__(self):
        return self.title

class Pattern(models.Model):
    entity=models.ForeignKey(Entity)
    pattern=models.CharField(max_length=200)

    def __unicode__(self):
        return self.pattern

class Bundle(models.Model):
    user=models.CharField(max_length=200)
    name=models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class BundleDoc(models.Model):
    bundle=models.ForeignKey(Bundle)
    doc_id=models.CharField(max_length=200)


