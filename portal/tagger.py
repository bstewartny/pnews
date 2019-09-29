from portal.models import *
import nltk
import re

class Tagger:
    
    @staticmethod
    def get_entity_candidates_for_text(text):
        a=[]
        for word in set(nltk.word_tokenize(text)):
            if word.isalnum():
                a.extend(Tagger.get_entity_candidates_for_word(word))
        return set(a)

    @staticmethod
    def extract_entities(text):
        entities=[]
        for entity in Tagger.get_entity_candidates_for_text(text):
            if Tagger.entity_matches_text(entity,text):
                entities.append(entity)
        return entities

    @staticmethod
    def pattern_re_matches_text(pattern_re,text):
        return pattern_re.search(text) is not None

    @staticmethod
    def pattern_res_match_text(pattern_res,text):
        for pattern_re in pattern_res:
            if Tagger.pattern_re_matches_text(pattern_re,text):
                return True
        return False

    @staticmethod
    def entity_matches_text(entity,text):
        return Tagger.pattern_res_match_text(Tagger.make_pattern_res([pattern.pattern for pattern in entity.pattern_set.filter(enabled=True)]),text)

    @staticmethod
    def get_entity_candidates_for_word(word):
        #TODO: this will return too many - need to match starts with word+' ' or matches exact (bug ignore case)`
        entities=set(Entity.objects.filter(enabled=True).filter(pattern__enabled=True).filter(pattern__pattern__istartswith=word))
        # NOTE: we do this hack in order to support tickers in format (xxx), (exchange:xxx) since the tokenization will currently remove the ( )
        entities=entities.union(set(Entity.objects.filter(enabled=True).filter(pattern__enabled=True).filter(pattern__pattern__iexact='('+word+')')))
        entities=entities.union(set(Entity.objects.filter(enabled=True).filter(pattern__enabled=True).filter(pattern__pattern__iendswith=':'+word+')')))
        return entities

    @staticmethod
    def make_pattern_res(patterns):
        return [Tagger.make_pattern_re(pattern) for pattern in patterns]

    @staticmethod
    def make_pattern_re(pattern):
        # make re to match begin/end of string or any non-word char as boundaries
        # TODO: make punctuation optional match (comma, periods, apostrophes)
        return re.compile('(^|[^\w])'+re.escape(pattern.strip())+'($|[^\w])',re.IGNORECASE)

    @staticmethod
    def get_candidate_documents(patterns):
        candidates=[]
        for pattern in patterns:
            candidates.extend(Document.objects.search(pattern))
        return candidates

    @staticmethod
    def process_entity(entity):
        tagged=Document.objects.filter(entities=entity)
        if tagged.count()>0:
            print('removing '+str(tagged.count())+' tagged documents for '+entity.name)
            # remove existing tags
            # TODO: can we do single bulk update/delete statement here?
            for doc in tagged:
                doc.entities.remove(entity)
                doc.save()

        patterns=[pattern.pattern for pattern in entity.pattern_set.filter(enabled=True)]
    
        if len(patterns)>0:
            
            candidates=Tagger.get_candidate_documents(patterns)
            
            candidate_set=set(candidates)
            num_candidates=len(candidate_set)
            #if num_candidates>0:
            #    print('found '+str(num_candidates)+' candidate documents for '+entity.name)
            
            re_patterns=Tagger.make_pattern_res(patterns)
            
            count=0
            
            for candidate in candidate_set:
                text=candidate.title
                if candidate.body:
                    text=text+' '+candidate.body
                if Tagger.pattern_res_match_text(re_patterns,text):
                    candidate.entities.add(entity)
                    candidate.save()
                    count=count+1
            if count>0:
                print('tagged '+str(count)+' documents for '+entity.name)
            
        entity.save()

