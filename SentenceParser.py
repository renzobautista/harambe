from bllipparser import RerankingParser

class SentenceParser():
    rrp = RerankingParser.fetch_and_load('WSJ-PTB3', verbose=True)

    @staticmethod
    def parse(sentence):
        return SentenceParser.rrp.simple_parse(sentence)