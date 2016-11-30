#!/usr/bin/python

# Usage: ./answer1.py src.txt q.txt
# input: 
#    - src.txt: source document to generate answers from
#    - q.txt: document containing n line-separated questions
# assumes input document paths are under the same working directory
#
# output:
#    - parsedQs.txt: document of n line-separated, parsed questions
#    - targetSentences.txt: document of n line-separated, parsed sentences. Each
#                           sentence is the most similar sentence, and thus the
#                           one we will draw the answer from, to the correspond-
#                           ing question in parsedQs.txt 
#    - tagging.txt: correctly formatted document containing n lines (n = # of 
#                   wh questions) of data to run the script sst.sh with
#    - original.txt: document containing information of mappings from parsed
#                    sentences to original sentences from src.txt, one each line
#
# ** KNOWN ISSUE **: 
# The John Reranking procedure in bllipparser sometimes causes a segfault - 
# documented here: https://github.com/BLLIP/bllip-parser/issues/49
# If this happens, please just run the same command again, and it should work.

import en
import re
import sys
import nltk
import string
import unicodedata
import treehelpers

from nltk.tokenize import sent_tokenize
from SentenceParser import SentenceParser
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer



sentences = []
global currprp
original = dict()
stemmer = SnowballStemmer("english")
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
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "does", "did", 
    "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven", 
    "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", 
    "everyone", "everything", "everywhere", "except", "few", "fifteen", "fifty", 
    "fill", "find", "fire", "first", "five", "for", "former", "formerly", 
    "forty", "found", "four", "from", "front", "full", "further", "get", "give",
    "go", "had", "has", "hasnt", "have", "he", "hence", "here", "hereafter",
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
  append(d)

  doc = d.read()
  doc=unicodedata.normalize('NFKD',doc.decode("utf8")).encode('ascii','ignore')
  
  qfile = open(args[1]).read()
  questions = parseQ(qfile.splitlines())

  global currprp
  currprp = ""
  parseDoc(doc)

  tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=stopwords)

  for q in questions:
    q = qtense(q)
    docNum = findDoc(q, tfidf)
    saveToFile(q, docNum)

  parsedQs.close()
  ts.close()
  tagging.close()
  o.close()



# return the first space-delimited word in the string
def first_word(string):
  result = ""
  for c in string:
    if c == " ":
      break
    else:
      result += c
  return result



# append words in the article title to the list of stop words (i.e. words to 
# ignore when doing tfidf calculations)
def append(d):
  first_line = d.readline()
  for w in first_line.split():
    w = w.replace("\n", "").lower()
    stopwords.append(w)



# tokenize function for sentences using the nltk snowball stemmer
def tokenize(text):
  tokens = nltk.word_tokenize(text)
  stems = []
  for t in tokens:
      stems.append(stemmer.stem(t))
  return stems



# generate array of parsed questions
def parseQ(qarray):
  ret = []

  for q in qarray:
    # get the actual question if composite sentence (i.e. has a comma)
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



# simple pronoun resolution: each sentence replaces the np pronoun with the np
# of the most recent sentence. Each time a sentence has a non-pronoun np, the 
# global tracker currprp is changed accordingly to keep track of the most
# recently seen np
def np_res(s):
  global currprp
  t = SentenceParser.parse(s)
  t = t[0]
  for i in xrange(len(t)):
    if(t[i].label() == 'NP'):
      lm = treehelpers.leftmost(t[i])
      if(lm.label() == 'PRP'):
        if(currprp != ""):
          s = s.replace(lm[0] + " ", currprp + " ", 1)
          return s
      else:
        currprp = lm[0]
        return s
  return s



# parses all sentence in the source document
def parseDoc(doc):
  sent = sent_tokenize(doc)
  for s in sent:
    if("\n" in s):
      tmp = s.splitlines()
      s = tmp[len(tmp)-1]
    s = np_res(s)
    # erase all content between parenthese to simplify
    s = re.sub(r' \((.*?)\)', "", s)
    snew = s.lower().translate(None, string.punctuation)
    sentences.append(snew)
    original[snew] = s
    o.write(snew + "  XIAOHANLANDREW  " + s + "\n")



# return the verb in the nltk tree
def tenseHelper(tree):
  for i in xrange(1, len(tree)):
    (word, tag) = tree[i]
    if(tag == 'VB' or tag == 'VBP'):
      return word
  return ""



# if a question is asking in past tense, e.g. "Who did we see last night?", find
# the main verb and replace it with its past tense form. The example question
# would be changed to "Who did we saw last night?"
# this change is done for parsing and word matching purposes
def qtense(q):
  qnew = q
  fw = first_word(qnew)

  if(fw in wh):
    qnew = qnew.replace(fw + " ", "")

  parsed = SentenceParser.parse(qnew).pos()
  (fw, first_tag) = parsed[0]
  if(first_tag == 'VBD'):
    v = tenseHelper(parsed)
    if(v != ""):
      vp = en.verb.past(v)
      q = q.replace(" " + v + " ", " " + vp + " ", 1)
      return q
    return q
  else:
    return q



# find the most relevant sentence from the source document that most closely
# matches the question
# algorithm: loop through all sentences and return the one with the highest
#            tfidf score with respect to the question
def findDoc(q, tfidf):
  maximum = -sys.maxint-1
  count = 0
  docNum = 0

  for s in sentences:
    tfidf_matrix = tfidf.fit_transform([q, s])
    cosine_sim = ((tfidf_matrix * tfidf_matrix.T).A)[0,1]

    if cosine_sim > maximum:
      docNum = count
      maximum = cosine_sim
    count += 1

  return docNum



# save the parsed question and sentence tagging information to the relevant
# files to be used by answer2.py
def saveToFile(q, docNum):
  parsedQs.write(q + "\n")
  targetSentence = sentences[docNum]
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
