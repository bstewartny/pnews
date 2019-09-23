import nltk

invalid_entities=['tweet text',
    'daily beast','javascript tag','trademark accessibility','white house','continue reading','written by','united states',
    'new york','new york city','new york times','washington post',
    'raw story','fox news','associated press','wall street','wall street journal','weekly standard']

def extract_entity_names(t):
  entity_names = []
  if hasattr(t,'label'):
      if t.label() == 'NE':
          entity_names.append(' '.join([child[0] for child in t]))
      else:
          for child in t:
              entity_names.extend(extract_entity_names(child))
  return entity_names

def is_substr(s,t):
  if len(t)<len(s):
    return False
  else:
    t=t.lower()
    return ((not t==s) and (t.startswith(s) or t.endswith(s)))

def has_substr(s,a):
  s=s.lower()
  for t in a:
    if is_substr(s,t):
      return True
  return False

def all_caps(s):
    return s.upper()==s

def filter_entities(a):
  u=[]
  a=list(set(a))
  # remove any single-word entities (too ambiguous in most cases)
  a=[s for s in a if len(s.split())>1]
  # remove any entities more than 2 words
  a=[s for s in a if len(s.split())<3]
  # remove any entities that are all CAPS
  a=[s for s in a if not all_caps(s)]
  a.sort(key=lambda x:len(x))
  a=[x for x in a if not has_substr(x,a)]
  a=[s for s in a if not s.lower() in invalid_entities]
  
  return a

def extract_entities(text):
  sentences = nltk.sent_tokenize(text)
  tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
  tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
  chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
  
  entity_names=[]
  for tree in chunked_sentences:
    entity_names.extend(extract_entity_names(tree))

  return filter_entities(entity_names)

