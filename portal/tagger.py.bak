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
        return Tagger.pattern_res_match_text(Tagger.make_pattern_res([pattern.pattern for pattern in entity.pattern_set.all()]),text)

    @staticmethod
    def get_entity_candidates_for_word(word):
        #TODO: this will return too many - need to match starts with word+' ' or matches exact (bug ignore case)`
        return set(Entity.objects.filter(enabled=True).filter(pattern__pattern__istartswith=word))

    @staticmethod
    def make_pattern_res(patterns):
        return [Tagger.make_pattern_re(pattern) for pattern in patterns]

    @staticmethod
    def make_pattern_re(pattern):
        # make re to match begin/end of string or any non-word char as boundaries
        return re.compile('(^|[^\w])'+pattern+'($|[^\w])',re.IGNORECASE)

    @staticmethod
    def get_candidate_documents(patterns):
        candidates=[]
        for pattern in patterns:
            candidates.extend(Document.objects.search(pattern))
        return candidates

    @staticmethod
    def process_entity(entity):
        tagged=Document.objects.filter(entities=entity)
        print 'found '+str(tagged.count())+' tagged documents'
        # remove existing tags
        # TODO: can we do single bulk update/delete statement here?
        for doc in tagged:
            doc.entities.remove(entity)
            doc.save()

        patterns=[pattern.pattern for pattern in entity.pattern_set.all()]
        
        candidates=Tagger.get_candidate_documents(patterns)
       
        print 'found '+str(len(set(candidates)))+' candidate documents'
        
        candidates.extend(tagged)

        re_patterns=Tagger.make_pattern_res(patterns)
        
        count=0
        
        for candidate in set(candidates):
            text=candidate.title
            if candidate.body:
                text=text+' '+candidate.body
            if Tagger.pattern_res_match_text(re_patterns,text):
                candidate.entities.add(entity)
                candidate.save()
                count=count+1
        print 'tagged '+str(count)+' documents with '+entity.name


