from nltk.tokenize import sent_tokenize

class TextParser():

    def __init__(self, filepath):
        file_content = open(filepath).read()
        self.content = self.__clean_content(file_content)


    def to_sentences(self):
        return sent_tokenize(self.content)

    def __clean_content(self, content):
        """
        Cleans the content to make it ready for tokenization.
        """
        non_ascii_removed = self.__remove_nonascii(content)
        short_lines_removed = self.__remove_short_lines(non_ascii_removed)
        return short_lines_removed

    def __remove_nonascii(self, content):
        rv = ""
        for line in content:
                line=line.decode("ascii","ignore").encode("ascii")
                if line=="":continue
                rv += line
        return rv

    def __remove_short_lines(self, content):
        """
        Removes the headers, which are not sentences.
        """
        rv = ""
        for line in content.splitlines():
            if len(line) > 80:
                rv += line + " "
        return rv