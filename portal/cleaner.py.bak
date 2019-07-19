import nltk
from BeautifulSoup import BeautifulSoup
import re

max_summary_len=400
min_sentence_len=20
max_sentence_len=300
min_clean_words=6
min_clean_words_ratio = 0.8
min_word_len=2
max_word_len=25

def clean_text(text):
    if text is None:
        return text
    else:
        return clean_summary(strip_html_tags(text))


def clean_sentence(sent):
  # remove date line
  # TODO: also look for unicode 'long dash' here...
  m=re.match('^.+--\s',sent)
  if m is not None:
    sent=sent[m.end():]
  return sent


def is_clean_word(word):
  if len(word)>max_word_len:
    return False
  if len(word)<min_word_len:
    return False
  if re.match('^[a-z]+$',word) is None and re.match('^[A-Z][a-z]+$',word) is None:
    return False
  return True

def is_clean_sentence(sent):
  if len(sent) < min_sentence_len:
    return False
  if len(sent) > max_sentence_len:
    return False
  if not sent[0].upper()==sent[0]:
    return False
  if not sent[-1]=='.':
    return False
  words=nltk.word_tokenize(sent)
  num_clean_words=len(filter(is_clean_word,words))
  if num_clean_words < min_clean_words:
    return False
  if float(num_clean_words) / float(len(words)) < min_clean_words_ratio:
    return False
  return True

def clean_summary(summary):
  # get one or two very clean sentences from the text
  if summary is None:
    return None
  if len(summary)==0:
    return None
  clean_sentences=[]
  total_len=0
  summary=summary.replace('&apos;','\'')
  for sentence in filter(is_clean_sentence,map(clean_sentence,nltk.sent_tokenize(summary))):
    if total_len+len(sentence) > max_summary_len and len(clean_sentences)>0:
      return ' '.join(clean_sentences)
    else:
      clean_sentences.append(sentence)
      total_len=total_len+len(sentence)
  
  if len(clean_sentences)>0:
    return ' '.join(clean_sentences)
  else:
    if len(summary)>200:
      return summary[:200]+'...'
    else:
      return summary

def strip_html_tags(html):
  # just get appended text elements from HTML
  try:
    text="".join(BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES).findAll(text=True))
    return text
  except:
    print 'Failed to strip html tags...'
    return html

