import sys
import nltk
import string

from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Assumes document containing n line-separated questions in the same path - 2nd arg
# Assumes document to pull answers from also in the same path - 1st arg
# http://www.bogotobogo.com/python/NLTK/tf_idf_with_scikit-learn_NLTK.php

stemmer = SnowballStemmer("english")
sentences = []


def main(args):
  doc = open(args[0]).read()
  q = open(args[1]).read()
  questions = q.splitlines()
  parseDoc(doc)

  tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
  tfidf_matrix = tfidf.fit_transform(sentences)

  print tfidf_matrix  
  # answer(questions)


def tokenize(text):
  tokens = nltk.word_tokenize(text)
  stems = []
  for t in tokens:
      stems.append(stemmer.stem(t))
  return stems


def parseDoc(doc):
  sent = sent_tokenize(doc)
  for s in sent:
    sentences.append(s.lower().translate(None, string.punctuation))


# def answer(questions):
#   for q in questions:
     # find the most likely sentence using tfidf and cosine similarity
     # yes/no question: match the answer by looking at the words and also POS
     #    answer yes if match, no if no match
     # other: identify keyword with POS and result of supersense tagging and replace


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Wrong number of arguments"
    sys.exit(0)
  else:
    main(sys.argv[1:])