from portal.models import *

class Highlighter:

    @staticmethod
    def highlight_text(text,query=None,entities=[],start_tag='<b>',end_tag='</b>'):
        words=Highlighter.get_highlight_words(query,entities)    
        text=' '+text+' '
        for word in words:
            text=Highlighter.highlight_word(text,word,start_tag,end_tag)
        return text.strip()

    @staticmethod    
    def get_highlight_words(query,entities=[]):
        words=[]
        if query:
            words.extend(query.split())
        if entities:
            for entity in entities:
                try:
                    if type(entity) is int:
                        entity=Entity.objects.get(id=entity)
                    if entity is not None:
                        words.append(entity.name)
                    for pattern in words.pattern_set.all():
                        words.append(pattern.pattern)
                except:
                    pass
        # TODO: deduplicate words, and sort by word length in desc order
        return set(words)
   
    @staticmethod    
    def highlight_word(text,word,start_tag='<b>',end_tag='</b>'):
        # TODO: handle other non-word seperators (period, comma, quote, etc.)
        # TODO: optimize by checking text length vs. word length and maybe check if word exists in text first...
        return text.replace(' '+word+' ',' '+start_tag+word+end_tag+' ')


        
