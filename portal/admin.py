from django.contrib import admin
from portal.models import *

"""
TODO:

    add comments
    add feed entities to new documents?
    add feed categories
    add entity categories
    add parent/child entities
    add category filters to feeds/entity admin lists
    add test page for text - tag with entities, and do NLP...
        highlight words to create new entities/patterns

    ajax forms for lookup and attach entities to feeds and documents
    for entity page - link to show all documents with that entity, show # of documents
    click on document to show test page (highlighted with entities, etc.)
    search page - add highlighting, facet navigation (checkboxes?), tag cloud
    
    topics page
        latest docs per top topics
    
    sources page
        latest docs per top sources

    

    charts/trends page
        # of documents per entity
        # per feed
        top N entities
        top N feeds
        trend of docs over past N days
        word cloud
        entity cloud
        feed cloud
        show pivot facets
            for top N facets
                show top N sub-facets for each one

    clustering
        run clustering job as celery task(s)
            perform k-means clustering, hierarchical, etc.
            group by cluster Id in search results
            expand clusters (show related)
            visualize clusters
            we need clusterID on document

    run tasks in celery
    add more feeds

    import entities:
        names
            congress/senate/exec branch
            CEOs
            world leaders
            polical commentators
        places
            us states and cities
            countries
                capital cities
        companies
            SP 500 names and tickers
        stuff from cia factbook
        
   add comments - search, reply, etc.
   select documents to add to bundle(s)
   search over bundles / navigate bundles
    share bundles with other users

   user login
      comments by user
      bundles for user
      permissions on feeds and documents

      file upload 
        extract text from binary (pdf,word)
        store binary blob (pdf, word, xls, ppt, etc.)
      create document (enter text)

      navigate results with prev/next full document with highlighting and comments
      send-to for each document (share, email, etc.)
      bookmarkable URLs for everything
      can use back button and refresh screen (same data)
      search result paging controls
      search result view (compact headline table, expanded headline+summary w/highlighting, full-page documents w/highlighting)

    
    deploy to server:
        we need hosted server:
            linux, 64bit
            cores: 8+
            RAM: 16GB+
            storage: 500GB+
        we need github for code:
            deploy to server from git
        we need database backup:
            daily backups, copy to S3 or dropbox

    need product name(s)

    need domain name(s)

    need site design template(s)

    need product home page - describe, show features and benefits

    show on HN








"""





def enable_entities(modeladmin,request,queryset):
    queryset.update(enabled=True)
enable_entities.short_description="Enable selected entities"

def disable_entities(modeladmin,request,queryset):
    queryset.update(enabled=False)
disable_entities.short_description="Disable selected entities"

def merge_entities(modeladmin,request,queryset):

    # TODO: how to take the one to merge to?
    # we can just take first one in list, or we can take shortest/longest name?
    if queryset.count()>1:
        first_one=queryset[0]
        others=[e for e in queryset if e!=first_one]
        first_one.merge(others)

merge_entities.short_description="Merge selected entities"

class PatternInline(admin.TabularInline):
    model=Pattern
    extra=3

class EntityAdmin(admin.ModelAdmin):
    search_fields=['name']
    list_display=('name','enabled','modified_date','num_docs')
    list_filter=['enabled','modified_date']
    inlines=[PatternInline]
    actions=[enable_entities,disable_entities,merge_entities]

class PatternAdmin(admin.ModelAdmin):
    search_fields=['pattern']
    list_display=('pattern','entity')

class FeedAdmin(admin.ModelAdmin):
    search_fields=['name']
    list_display=('name','url','num_docs')
    filter_horizontal=['entities']

class DocumentAdmin(admin.ModelAdmin):
    search_fields=['title']
    list_display=('title','feed','pub_date','modified_date','num_entities')
    list_filter=['pub_date','modified_date']
    filter_horizontal=['entities']
    readonly_fields=['highlighted']
    fields=['feed','title','url','entities','highlighted']


admin.site.register(Entity,EntityAdmin)
admin.site.register(Pattern,PatternAdmin)
admin.site.register(Feed,FeedAdmin)
admin.site.register(Document,DocumentAdmin)


