from TextParser import TextParser
from SentenceParser import SentenceParser
from SentencesPreprocessor import SentencesPreprocessor
from treehelpers import *

sentences = TextParser("data/set1/a1.txt").to_sentences()[:50]
simple_sentences = SentencesPreprocessor(sentences).generate_simple_sentences()
for sentence in simple_sentences:
  for t in sentence:
    if t.label() == 'VP':
      print immediate_labels(t)
      print sentence_join(t)
      for s in t:
        if s.label() == 'VP':
          print immediate_labels(s)
          print sentence_join(s)
