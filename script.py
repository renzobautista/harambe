from TextParser import TextParser
from SentenceParser import SentenceParser
from SentencesPreprocessor import SentencesPreprocessor

sentences = TextParser("data/set1/a1.txt").to_sentences()[:50]
simple_sentences = SentencesPreprocessor(sentences).generate_simple_sentences()