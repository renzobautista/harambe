#!/usr/bin/python


import en
import re
import sys
import json
import nltk
import string
import unicodedata
import treehelpers

from nltk.tree import ParentedTree
from SentenceParser import SentenceParser
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Assumes document containing n line-separated questions in the same path - 2nd arg
# Assumes document to pull answers from also in the same path - 1st arg
# http://www.bogotobogo.com/python/NLTK/tf_idf_with_scikit-learn_NLTK.php

# https://github.com/BLLIP/bllip-parser/issues/50

stemmer = SnowballStemmer("english")
sentences = []
original = dict()
tagged = open("tagging.txt.pred.sst")
wh = ["who", "what", "when", "where", "how", "why", "which", "whose"]
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
    "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
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
  append(d)
  # print stopwords
  doc = d.read()
  doc = unicodedata.normalize('NFKD', doc.decode("utf8")).encode('ascii','ignore')
  # qfile = open(args[1]).read()
  # questions = parseQ(qfile.splitlines())
  questions = readQ()
  parseDoc(doc)

  tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=stopwords)
  # tfidf = TfidfVectorizer(tokenizer=tokenize)

  count = 0
  for q in questions:
    # q = qtense(q)
    # print q
    # fw = first_word(q)
    # q = q.replace(fw + " ", "")
    # docNum = findDoc(q, tfidf)
    answer(q, count, tfidf)
    count += 1
  
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


def readQ():
  q = open("parsedQs.txt").read()
  return q.splitlines()


def parseDoc(doc):
  # sent = sent_tokenize(doc)
  # # print "\nSource:"
  # for s in sent:
  #   # print s
  #   snew = s.lower().translate(None, string.punctuation)
  #   # sentences.append(snew)
  #   original[snew] = s

  o = open("original.txt").read().splitlines()
  for l in o:
    words = l.split("  XIAOHANLANDREW  ")
    original[words[0]] = words[1]

  tmp = open("targetSentences.txt").read().splitlines()
  for i in xrange(len(tmp)):
    sentences.append(tmp[i])
  # print "sentences: ", sentences


def contained(q, s):
  # print "in contained"
  # print "q: ", q
  s = s.lower().translate(None, string.punctuation)
  # print "s: ", s
  # tfidf.fit_transform([q])
  # fsq = tfidf.get_feature_names()
  # print "fsq: ", fsq
  q1 = q.split()
  # print "q1: ", q1
  for w in q1:
    if(w not in stopwords):
      if(w not in s):
        # print "not w: ", w
        return False
  return True


def sentfromleaves(t):
  return " ".join(t.leaves()).replace(" 's ", "'s ")



def whoHelper(fw, q, stp, t, tfidf):
  stitch = fw + " " + q
  tstitch = SentenceParser.parse(stitch)
  # tstitch.draw()
  rest = tstitch[0][1]
  if(len(rest) == 1):
    rest = rest[0]
  # rest.draw()
  # print len(rest)==3
  if(len(rest) == 2 and 'VB' in rest[0].label() and rest[1].label() == 'NP'):
    ret = ""
    tstp = SentenceParser.parse(stp)[0]
    for i in xrange(len(tstp)):
      if(tstp[i].label() == 'NP'):
        ret = treehelpers.leftmost(t[i])[0]
    
    if(rest[0][0] in ["is", "was", "were", "are"]):
      find = stp.split(rest[0][0] + " ")[1]
      first = SentenceParser.parse(find)[0]
      for i in xrange(len(first)):
        if(first[i].label() == 'NP'):
          n2 =  sentfromleaves(first[i])
          rest1 = sentfromleaves(rest)

          tfidf_matrix = tfidf.fit_transform([ret, rest1])
          cosine_sim1 = ((tfidf_matrix * tfidf_matrix.T).A)[0,1]

          tfidf_matrix = tfidf.fit_transform([n2, rest1])
          cosine_sim2 = ((tfidf_matrix * tfidf_matrix.T).A)[0,1]

          # print "pos1: ", pos1
          # print "pos2: ", pos2
          # print "cs1: ", cosine_sim1
          # print "cs2: ", cosine_sim2

          if cosine_sim1 > cosine_sim2:
            return n2
          else:
            return ret
    return ret
  
  elif(len(rest) == 3 and rest[2].label() == 'VP'):
    # print "three"
    aux = treehelpers.leftmost(rest)[0]
    if(aux in ["does", "did", "do"]):
      verb = treehelpers.leftmost(rest[2])[0]
      # print "verb: ", verb
      if(aux=="did"):
        verb = en.verb.past(verb)
        # print "past: ", verb
      l = ""
      tmp = stp.split(verb + " ")
      if(first_word(stp) == verb):
        l = tmp[0]
      else:
        l = tmp[1]
      first = SentenceParser.parse(l)[0]
      # first.draw()
      # for i in xrange(len(first)):
      #   if(first[i].label() == 'NP'):
      #     return sentfromleaves(first[i])
      nps = list(first.subtrees(filter=lambda x: x.label()=='PP'))
      return sentfromleaves(nps[0])
    else:
      return stp


def parsetd(superS):
  td = dict()
  for i in superS.keys():
    (word, tag) = superS[i]
    td[word] = tag
  return td


def whAnswer(fw, q, ts, tfidf):
  whenere = tagged.readline()

  s = original[ts]
  # print "before: ", s
  # s = re.sub(r' \((.*?)\)', "", s)
  # print "after: ", s
  # chunkS = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(s)))
  # print "super: ", superS
  # print "chunk: ", chunkS

  t = SentenceParser.parse(s)
  ss = reversed(list(t.subtrees(filter=lambda x: x.label()=='S')))
  # print "ss: ", ss
  for st in ss:
    # print "st: ", st
    stp = sentfromleaves(st)
    # print "stp: ", stp
    if(contained(q, stp)):
      # print "stp: ", stp

      if(fw == "who"):
        ret = whoHelper(fw, q, stp, t, tfidf)
        if(ret != None and ret != ""):
          return ret


      elif(fw == "what" or fw == "which"):
        if(fw == "what" and "happen" in first_word(q)):
          return stp
        ret = whoHelper(fw, q, stp, t, tfidf)
        if(ret != None and ret != ""):
          return ret



      elif(fw == "when" or fw == "where"):
        superS = json.loads(whenere.split("\t")[2])["labels"]
        td = parsetd(superS)
        tstp = SentenceParser.parse(stp)
        pps = list(tstp.subtrees(filter=lambda x: x.label()=='PP'))
        pts = list()
        for p in pps:
          pts.append(sentfromleaves(p))
        
        keyword = ""
        nopp = []
        if(fw == "when"):
          keyword = "TIME"
        else:
          keyword = "LOCATION"

        matched = filter(lambda x: td[x]==keyword, td.keys())
        nechunk = ["FACILITY", "GPE", "GSP", "LOCATION", "ORGANIZATION", "PERSON"]

        if(len(matched) != 0):
          likely = list()
          print matched
          print pts
          for m in matched:
            for p in pts:
              if(m in p):
                if(fw == "when"):
                  return p
                likely.append(p)
          if(fw == "where"):
            for l in likely:
              chunktags = nltk.ne_chunk(SentenceParser.parse(l).pos())
              ctl = map(lambda x: x.label(), list(chunktags.subtrees()))
              ctl = filter(lambda x:x in nechunk, ctl)
              ctl = filter(lambda x: x != 'PERSON', ctl)
              if(len(ctl) != 0):
                return l


      elif(fw == "how"):
        tstp = SentenceParser.parse(stp)
        pt = tstp.pos()

        tq = SentenceParser.parse(q)[0]
        while(len(tq) <= 1):
          if(len(tq) == 0):
            break
          tq = tq[0]
        if(len(tq) > 1):
          tq = tq[1:]
          for i in xrange(len(tq)):
            if(tq[i].label() == 'VP'):
              vs = list(tq[i].subtrees(filter=lambda x: 'VB' in x.label()))
              verb = vs[0][0]
              # print "verb: ", verb
              for j in xrange(len(pt)):
                (w, l) = pt[j]
                if(w==verb):
                  # print "w: ", w
                  # print "pt: ", pt
                  c = j
                  if(c > 0):
                    c -= 1
                    ret = ""
                    while(c >= 0):
                      # print "first while"
                      (w1, l1) = pt[c]
                      if('RB' in l1):
                        ret = w1 + " " + ret
                        c -= 1
                        # print "ret1: ", ret
                      else:
                        break
                    if(ret != ""):
                      return ret
                  if(c < len(pt)):
                    c += 1
                    ret = ""
                    while(c < len(pt)):
                      # print "second while"
                      (w1, l1) = pt[c]
                      if('RB' in l1):
                        ret = ret + " " + w1
                        c += 1
                        # print "ret2: ", ret
                      else:
                        break
                    if(ret != ""):
                      return ret

        qnew = q
        sqnew = SentenceParser.parse(qnew)[0]
        for i in xrange(len(sqnew)):
          if(sqnew[i].label() == 'VP'):
            qnew = sentfromleaves(sqnew[i])
        tstp1 = ParentedTree.convert(tstp)
        pps = list(tstp1.subtrees(filter=lambda x: x.label()=='PP'))
        for p in pps:
          tmp = p.parent()
          while(tmp.label() != 'S'):
            if(tmp.label() == 'VP'):
              tmps = sentfromleaves(tmp)
              if(contained(qnew, tmps)):
                return tmps
            tmp = tmp.parent()
      



      elif(fw == "why"):
        tstp = SentenceParser.parse(stp)
        if("because of " in stp or "Because of " in stp):
          pps = list(tstp.subtrees(filter=lambda x: x.label()=='PP'))
          for p in pps:
            if((p[0][0]=="because" or p[0][0]=="Because") and p[1][0]=="of"):
              return sentfromleaves(p)
          return stp
        elif("because " in stp or "Because " in stp):
          sbars = list(tstp.subtrees(filter=lambda x: x.label()=='SBAR'))
          for sbar in sbars:
            if(sbar[0][0]=="because" or sbar[0][0]=="Because"):
              return sentfromleaves(sbar)
          return stp
        elif("for " in stp):
          sbars = list(tstp.subtrees(filter=lambda x: x.label()=='SBAR'))
          for sbar in sbars:
            if(sbar[0][0]=="for"):
              return sentfromleaves(sbar[1])
          return stp
        elif("since " in stp or "Since " in stp):
          sbars = list(tstp.subtrees(filter=lambda x: x.label()=='SBAR'))
          for sbar in sbars:
            if(sbar[0][0]=="since" or sbar[0][0]=="Since"):
              return sentfromleaves(sbar[1])
        elif("so that " in stp):
          sbars = list(tstp.subtrees(filter=lambda x: x.label()=='SBAR'))
          for sbar in sbars:
            if(sbar[0][0]=="so" and sbar[1][0]=="that"):
              return sentfromleaves(sbar)
          return stp
        elif("so " in stp or "So " in stp):
          sbars = list(tstp.subtrees(filter=lambda x: x.label()=='SBAR'))
          for sbar in sbars:
            if(sbar[0][0]=="so" or sbar[0][0]=="So"):
              return sentfromleaves(sbar)
      
      else:
        return stp

  return ""


def answer(q, count, tfidf):
  # print "count: ", count
  # print "sentences: ", sentences
  targetSentence = sentences[count]
  print "Question (parsed): ", q
  print "Target sentence (parsed): ", targetSentence
  fw = first_word(q)
  # print fw
  q = q.replace(fw + " ", "")
  # print q
  if (fw not in wh):
    # yes/no question
    tfidf.fit_transform([q])
    # print q
    fsq = set(tfidf.get_feature_names())
    # print fw
    # print set(fw)
    tfidf.fit_transform([targetSentence])
    fst = set(tfidf.get_feature_names())
    # print "fsq: ", fsq, "fst: ", fst
    if(fsq.issubset(fst)):
      print "Yes.\n"
    else:
      print "No.\n"
     # evaluate: ???? train some data set
     # think of different metrics to get the target sentence
     # document about is the grass not green?
  else:
    # wh question

    # pronoun: coreference resolution
    # beautify answer

    # change directory
    # make new file containing the correctly formatted POS tagged string
    # run sst.sh with file
    # look at output
    # fall-through: return target string

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
    if(len(targetSentence.split()) <= len(q.split())):
      # original answer is short enough
      print original[targetSentence]

    else:
      ret = ""
      try:
        ret = whAnswer(fw, q, targetSentence, tfidf)
      except IndexError:
        ret = ""

      # print "ret: ", ret
      if(ret == ""):
        # fall through
        # if the original sentence is within a certain threshold
        print original[targetSentence]
      else:
        ret = ret.strip()
        if(ret[0].islower()):
          ret = ret[0].upper() + ret[1:]
        if('.' not in ret):
          ret = ret+'.'
        print ret
    print "\n"


if __name__ == '__main__':
  # print "in 2\n"
  # print (sys.argv)
  if len(sys.argv) != 3:
    print "Wrong number of arguments"
    sys.exit(0)
  else:
    main(sys.argv[1:])
