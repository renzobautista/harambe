from TextParser import TextParser
from SentenceParser import SentenceParser

sentences = TextParser('data/set1/a1.txt').to_sentences()
for sentence in sentences:
    SentenceParser.parse(sentence)