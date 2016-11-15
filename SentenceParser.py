from bllipparser import RerankingParser
from nltk.tree import Tree

class SentenceParser():
    rrp = RerankingParser.fetch_and_load('WSJ-PTB3', verbose=False)

    @staticmethod
    def parse(sentence):
        return Tree.fromstring(SentenceParser.rrp.simple_parse(sentence))