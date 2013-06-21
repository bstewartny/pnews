from portal.models import *
import nltk

def extract_entities(text):
   
    text=text.lower()

    words=nltk.word_tokenize(text)
    
    entities=[]
    
    entity_candidates=[]
    
    for word in set(words):
        if word.isalnum():
            entity_candidates.extend(get_entity_candidates(word))
       
    entity_candidates=set(entity_candidates)
    print 'found '+str(len(entity_candidates)) +' entity candidates'
    for entity in entity_candidates:
        if entity_matches_text(entity,text):
            entities.append(entity)
    return entities


def entity_matches_text(entity,text):
    for pattern in entity.pattern_set.all():
        try:
            i=text.index(pattern.pattern.lower())
            # make sure prev/next chars are not alpha-numeric
            if i>-1:
                if i>0:
                    prev_char=text[i-1]
                    if prev_char.isalnum():
                        print 'prev char is not alnum: '+prev_char
                        continue

                if i+len(pattern.pattern)<len(text)-1:
                    next_char=text[i+len(pattern.pattern)]
                    if next_char.isalnum():
                        print 'next char is not alnum: '+next_char
                        continue
                print 'entity '+entity.name +' matches with pattern: '+pattern.pattern
                return True
        except:
            continue
    print 'entity candidate '+entity.name+' failed to match text'
    return False


def get_entity_candidates(word):
    # TODO: cache entity candidates for this word and lookup in cache next time
    return set(Entity.objects.filter(enabled=True).filter(pattern__pattern__startswith=word+' ') | Entity.objects.filter(enabled=True).filter(pattern__pattern=word))

