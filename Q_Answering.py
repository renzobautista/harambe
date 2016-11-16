import sys
import nltk
import string

from SentenceParser import SentenceParser
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Assumes document containing n line-separated questions in the same path - 2nd arg
# Assumes document to pull answers from also in the same path - 1st arg
# http://www.bogotobogo.com/python/NLTK/tf_idf_with_scikit-learn_NLTK.php

stemmer = SnowballStemmer("english")
sentences = []
wh = ["Who", "What", "When", "Where", "How", "Why"]


def main(args):
  doc = open(args[0]).read()
  qfile = open(args[1]).read()
  questions = parseQ(qfile.splitlines())
  parseDoc(doc)

  # tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
  tfidf = TfidfVectorizer(tokenizer=tokenize)

  for q in questions:
    docNum = findDoc(q, tfidf)
    answer(q, docNum, tfidf)
  
  # print tfidf_matrix  


def first_word(string):
  result = ""
  for c in string:
    if c == " ":
      break
    else:
      result += c

  return result


def tokenize(text):
  tokens = nltk.word_tokenize(text)
  stems = []
  for t in tokens:
      stems.append(stemmer.stem(t))
  return stems


def parseQ(qarray):
  ret = []
  for q in qarray:
    # get the actual question if composite sentence
    if(', ' in q):
      qsplit = q.split(', ')
      s1 = SentenceParser.parse(qsplit[0])[0].label()
      s2 = SentenceParser.parse(qsplit[1])[0].label()
      s1b = False
      s2b = False
      if(s1 == "SQ" or s1 == "SQARQ"):
        ret.append(qsplit[0].lower().translate(None, string.punctuation)) 
        s1b = True
      if(s2 == "SQ" or s2 == "SQARQ"):
        ret.append(qsplit[1].lower().translate(None, string.punctuation)) 
        s2b = True

      # fall through case
      if(not(s1b or s2b)):
        ret.append(qsplit[0].lower().translate(None, string.punctuation))

    
    else:
      ret.append(q.lower().translate(None, string.punctuation)) 
  return ret


def parseDoc(doc):
  sent = sent_tokenize(doc)
  print "\nSource:"
  for s in sent:
    print s
    sentences.append(s.lower().translate(None, string.punctuation))
  print "\n"


def findDoc(q, tfidf):
  maximum = -sys.maxint-1
  count = 0
  docNum = 0

  for s in sentences:
    tfidf_matrix = tfidf.fit_transform([q, s])
    cosine_sim = ((tfidf_matrix * tfidf_matrix.T).A)[0,1]
    # print "s: ", s
    # print "cosine: ", cosine_sim

    if cosine_sim > maximum:
      docNum = count
      maximum = cosine_sim
    count += 1

  return docNum


def answer(q, docNum, tfidf):
  targetSentence = sentences[docNum]
  print "Question (parsed): ", q
  print "Target sentence (parsed): ", targetSentence
  if (first_word(q) not in wh):
    # yes/no question
    tfidf.fit_transform([q])
    fsq = tfidf.get_feature_names()
    fst = targetSentence.split()
    if(set(fsq).issubset(set(fst))):
      print "Answer: Yes. \n"
    else:
      print "Answer: No. \n"

     # find the most likely sentence using tfidf and cosine similarity
     # yes/no question: match the answer by looking at the words and also POS
     #    answer yes if match, no if no match
     # other: identify keyword with POS and result of supersense tagging and replace
     # evaluate: ???? train some data set
     # think of different metrics to get the target sentence
     # is the grass not red?
  else:
    # wh question
    # if in the form of wh/word + SQ (ex. when did you eat), look at tense of second word in SQ 
    pass


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Wrong number of arguments"
    sys.exit(0)
  else:
    main(sys.argv[1:])