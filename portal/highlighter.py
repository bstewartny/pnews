from portal.models import *
import re

class Highlighter:

    @staticmethod
    def highlight_text(text,query=None,entities=[],start_tag='<b>',end_tag='</b>'):
        patterns=Highlighter.get_highlight_patterns(query,entities)    
        text=' '+text+' '
        for pattern in patterns:
            text=Highlighter.highlight_re(text,pattern,start_tag,end_tag)
        return text.strip()

    @staticmethod
    def get_highlight_patterns(query,entities=[]):
        return [Highlighter.get_word_pattern(word) for word in Highlighter.get_highlight_words(query,entities)]

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
                    for pattern in entity.pattern_set.filter(enabled=True):
                        words.append(pattern.pattern)
                except:
                    pass
        # TODO: deduplicate words, and sort by word length in desc order
        return sorted(set(words),key=len,reverse=True)
   
    @staticmethod
    def highlight_re(text,pattern,start_tag='<b>',end_tag='</b>'):
        return pattern.sub(start_tag+"\\1"+end_tag,text)
    
    @staticmethod
    def get_word_pattern(text):
        # TODO: ignore punctuation
        return re.compile('('+re.escape(text)+')',re.IGNORECASE)
    
    @staticmethod    
    def highlight_word(text,word,start_tag='<b>',end_tag='</b>'):
        print('highlight_word: word='+word+', text='+text)
        return Highlighter.highlight_re(text,Highlighter.get_word_pattern(text),start_tag,end_tag)


        
