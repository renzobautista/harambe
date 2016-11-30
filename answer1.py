#!/usr/bin/python


import en
import os
import re
import sys
import nltk
import string
import subprocess
import unicodedata
import treehelpers

from SentenceParser import SentenceParser
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Assumes document containing n line-separated questions in the same path - 2nd arg
# Assumes document to pull answers from also in the same path - 1st arg
# http://www.bogotobogo.com/python/NLTK/tf_idf_with_scikit-learn_NLTK.php

# https://github.com/BLLIP/bllip-parser/issues/49

stemmer = SnowballStemmer("english")
sentences = []
global currprp
original = dict()
wh = ["who", "what", "when", "where", "how", "why", "which", "whose"]

parsedQs = open("parsedQs.txt", "w")
ts = open("targetSentences.txt", "w")
tagging = open("tagging.txt", "w")
o = open("original.txt", "w")

stopwords = [
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
    "around", "as", "at", "back", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
    "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
    "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
    "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fifty", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "hasnt", "have", "he", "hence", "here", "hereafter",
    "hereby", "herein", "hereupon", "hers", "herself", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me",
    "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
    "move", "much", "must", "my", "myself", "name", "namely", "neither",
    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "nothing", "now", "nowhere", "of", "off", "often", "on",
    "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
    "please", "put", "rather", "re", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should", "show", "side",
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
    "third", "this", "those", "though", "three", "through", "throughout",
    "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby",
    "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
    "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves"]


def main(args):
  d = open(args[0])
  # print "1"
  append(d)
  # print "2"
  # print stopwords
  doc = d.read()
  # print "3"
  doc = unicodedata.normalize('NFKD', doc.decode("utf8")).encode('ascii','ignore')
  # print "4"
  qfile = open(args[1]).read()
  # print "5"
  questions = parseQ(qfile.splitlines())
  # print "6"
  global currprp
  currprp = ""
  parseDoc(doc)
  # print "7"

  tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=stopwords)
  # tfidf = TfidfVectorizer(tokenizer=tokenize)

  for q in questions:
    q = qtense(q)
    # print q
    # fw = first_word(q)
    # q = q.replace(fw + " ", "")
    docNum = findDoc(q, tfidf)
    saveToFile(q, docNum)

  # print "8"
  parsedQs.close()
  ts.close()
  tagging.close()
  o.close()
  # print "9"

  # print tfidf_matrix  


def first_word(string):
  result = ""
  for c in string:
    if c == " ":
      break
    else:
      result += c

  return result


def append(d):
  first_line = d.readline()
  for w in first_line.split():
    w = w.replace("\n", "").lower()
    stopwords.append(w)


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


def np_res(s):
  # print "here"
  global currprp
  # print "middle?"
  # print "s: ", s
  t = SentenceParser.parse(s)
  # print "there"
  t = t[0]
  # print "nowhere"
  for i in xrange(len(t)):
    # print "looping"
    if(t[i].label() == 'NP'):
      lm = treehelpers.leftmost(t[i])
      # print "found"
      if(lm.label() == 'PRP'):
        if(currprp != ""):
          s = s.replace(lm[0] + " ", currprp + " ", 1)
          return s
      else:
        currprp = lm[0]
        return s
  return s


def parseDoc(doc):
  sent = sent_tokenize(doc)
  # print "sent: ", sent
  # print "\nSource:"
  for s in sent:
    # print s
    if("\n" in s):
      # print "where's this n?"
      tmp = s.splitlines()
      s = tmp[len(tmp)-1]
    # simple pronoun coresolution
    # print "sanity"
    s = np_res(s)
    # print "shmer"
    s = re.sub(r' \((.*?)\)', "", s)
    snew = s.lower().translate(None, string.punctuation)
    # print "snew: ", snew
    sentences.append(snew)
    original[snew] = s
    o.write(snew + "  XIAOHANLANDREW  " + s + "\n")
  # print "\n"


def tenseHelper(tree):
  # print "tree: ", tree
  # if(len(tree) == 1):
  #   if(tree.label() == 'VB' or tree.label() == 'VBP'):
  #     return tree[0]
  #   else:
  #     return ""
  # for i in xrange(len(tree)):
  #   t = tenseHelper(tree[i])
  #   if(t != ""):
  #     return t
  # return ""
  for i in xrange(1, len(tree)):
    (word, tag) = tree[i]
    if(tag == 'VB' or tag == 'VBP'):
      return word
  return ""


def qtense(q):
  # tense for wh questions:
    # Who did we see last night?
    # Who wrote the poem?

  # print "here: ", q
  qnew = q
  fw = first_word(qnew)
  if(fw in wh):
    qnew = qnew.replace(fw + " ", "")
  parsed = SentenceParser.parse(qnew).pos()
  (fw, first_tag) = parsed[0]
  # print "parsed: ", parsed
  # print first_tag
  if(first_tag == 'VBD'):
    # print "past"
    # find main verb if any
    # get past tense
    # replace verb with past tense
    v = tenseHelper(parsed)
    # print "v: ", v
    if(v != ""):
      # print "here?"
      # print "verb to change: ", v
      vp = en.verb.past(v)
      # print "vp: ", vp
      q = q.replace(" " + v + " ", " " + vp + " ", 1)
      # print "changed q: ", q
      return q
    return q
  else:
    return q


def findDoc(q, tfidf):
  maximum = -sys.maxint-1
  count = 0
  docNum = 0

  for s in sentences:
    # print q, s
    tfidf_matrix = tfidf.fit_transform([q, s])
    cosine_sim = ((tfidf_matrix * tfidf_matrix.T).A)[0,1]
    # print "s: ", s
    # print "cosine: ", cosine_sim

    if cosine_sim > maximum:
      docNum = count
      maximum = cosine_sim
    count += 1

  return docNum


def saveToFile(q, docNum):
  parsedQs.write(q + "\n")
  # print "sentences: ", sentences
  targetSentence = sentences[docNum]
  # print "targetSentence: ", targetSentence
  ts.write(targetSentence + "\n")
  if(first_word(q) in wh):
    p = SentenceParser.parse(original[targetSentence]).pos()
    for i in xrange(len(p)):
      (w, t) = p[i]
      tagging.write(w + "\t" + t + "\n")
    tagging.write("\n")


if __name__ == '__main__':
  # print (sys.argv)
  if len(sys.argv) != 3:
    print "Wrong number of arguments"
    sys.exit(0)
  else:
    main(sys.argv[1:])
