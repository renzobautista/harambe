import string

from SentenceParser import SentenceParser


def _ascii_word(word):
    for c in word:
        if c not in string.ascii_letters:
            return False
    return True


def _is_stop_char(c):
    return c == '.' or c == '?' or c == ',' or c == ' '


def _tree_to_string(tree):
    result = ''
    for word in tree.tokens():
        if not _is_stop_char(word):
            result += ' '
        result += word
    return result.strip()


# Returns the negation of a yes/no question so that it becomes a declarative
# statement. This overall function is kinda hacky.
def negate_question(sentence):
    parse_tree = SentenceParser.tree_parse(sentence)
    try:
        num_trees = len(parse_tree[0])
        sub_phrases = [None] * num_trees
    except:
        print 'Improper sentence; negation failed'
        return 'Improper sentence!'

    for i in range(num_trees):
        sub_phrases[i] = _tree_to_string(parse_tree[0][i])

    result = ''
    sub_phrases[0], sub_phrases[1] = sub_phrases[1], sub_phrases[0]

    # Kinda hacky (handling capitalization)

    # Uppercase first letter of current start
    result += sub_phrases[0][0].upper()
    result += sub_phrases[0][1:]

    if not _is_stop_char(sub_phrases[1][0]):
        result += ' '
    # Lowercase first letter of initial start
    result += sub_phrases[1][0].lower()
    result += sub_phrases[1][1:]

    for phrase in sub_phrases[2:]:
        if not _is_stop_char(phrase[0]):
            result += ' '
        result += phrase

    result = result.strip()
    return result[:-1] + '.'


if __name__ == '__main__':
    print negate_question('Is Harambe, the stupid cat, a fat dog?')
    print negate_question('Do you have a life?')
    print negate_question('Have you eaten?')
    print negate_question('Was it raining?')
