import itertools
import json
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'pnews.settings'

if django.VERSION[1] > 6:
    django.setup()

from portal.models import *

# synonyms we should expand to create variations of company names
syn_list=[['inc','incorporated'],['ltd','limited'],['corp','corporation'],['comp','company'],['intl','international']]
syn_map={}

for syn in syn_list:
    for v in syn:
        syn_map[v]=syn

# generate a permutations matrix we can feed into the 'product' function 
def gen_matrix(sentence):
    words=sentence.split()
    matrix=[]

    for word in words:
        if word.lower() in syn_map:
            matrix.append(syn_map[word.lower()])
        else:
            matrix.append([word])
    return matrix

def generate_company_name_patterns(name):
    # strip away commas and periods
    patterns=[]
    name=name.strip()
    # remove commas
    name=name.replace(',','')
    # remove extra spaces
    name=name.replace('  ',' ')
    # remove trailing period ("Acme Inc.", etc.)
    if name.endswith('.'):
        name=name[:-1]
    
    # generate matrix of permutations from the syn_map
    matrix=gen_matrix(name)
    for s in itertools.product(*matrix):
        pattern=' '.join(s).replace('  ',' ').strip()
        print('company pattern: '+pattern)
        patterns.append(pattern)
    return patterns


def load_companies(filename,name_field,sector_field,ticker_field):
    print('load_companies: '+filename)
    f=open(filename)
    companies=json.load(f)
    c=0
    for company in companies:
        name=company.get(name_field)
        if not name:
            continue
        name=name.strip()
        if len(name)>50:
            continue
        if name.endswith(' ETF'):
            continue
        if sector_field:
            sector=company.get(sector_field)
        else:
            sector=None
        ticker=company.get(ticker_field)
        if not ticker:
            continue
        create_company_entity(ticker,name,sector)
        c+=1
    
    f.close()
    print('loaded '+str(c)+' companies from: '+filename)

def get_ticker_patterns(ticker):
    exchange_prefixes=['','NYSE:','NASD:','NASDAQ:','AMEX:']
    
    return ['('+prefix+ticker+')' for prefix in exchange_prefixes]

def create_company_entity(ticker,name,sector):
    
    company_patterns=generate_company_name_patterns(name)
    company_patterns.extend(get_ticker_patterns(ticker))
    company_entity=get_or_create_entity('company',name,patterns=company_patterns)
    
    if sector:
        sector_entity=get_or_create_entity('sector',sector,patterns=[sector+' sector'])
        if not company_entity.parent==sector_entity:
            company_entity.parent=sector_entity
            company_entity.save() 

def get_or_create_entity(entity_type,name,patterns):
    et=EntityType.objects.filter(name__iexact=entity_type).first()
    if et is None:
        et=EntityType(name=entity_type)
        et.save()

    entity=Entity.objects.filter(entity_type=et,name__iexact=name).first()
    if entity is None:
        print('Creating new entity: '+entity_type+': '+name)
        entity=Entity(entity_type=et,name=name)
        entity.save()
    else:
        print('Entity: '+entity_type+': '+name+' already exists.')

    if patterns:
        for pattern in patterns:
            if not entity.pattern_set.filter(pattern__iexact=pattern).exists():
                print('Creating new entity pattern: '+pattern)
                p=Pattern(pattern=pattern)
                p.entity=entity
                # if pattern is single alphanumeric word do not enable it
                if pattern.isalnum():
                    if len(pattern.split())==1:
                        p.enabled=False
                p.save()

    return entity

if __name__=='__main__':
    # sp500
    # https://pkgstore.datahub.io/core/s-and-p-500-companies/constituents_json/data/64dd3e9582b936b0352fdd826ecd3c95/constituents_json.json
    load_companies('sp500-constituents.json',name_field='Name',sector_field='Sector',ticker_field='Symbol')
    # nasdaq
    # https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_json/data/a5bc7580d6176d60ac0b2142ca8d7df6/nasdaq-listed_json.json
    load_companies('nasdaq-constituents.json',name_field='Company Name',sector_field=None,ticker_field='Symbol')
    
