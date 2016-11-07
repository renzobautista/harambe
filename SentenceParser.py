from bllipparser import RerankingParser

class SentenceParser():
    rrp = RerankingParser.fetch_and_load('WSJ-PTB3', verbose=True)

    @staticmethod
    def parse(sentence):
        return SentenceParser.rrp.simple_parse(sentence)

    @staticmethod
    def tree_parse(sentence):
        return (SentenceParser.all_parses(sentence)[0]).ptb_parse

    @staticmethod
    def all_parses(sentence):
        return SentenceParser.rrp.parse(sentence)
