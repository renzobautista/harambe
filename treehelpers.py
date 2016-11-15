from nltk.tree import Tree

def sentence_join(t):
  word_list = t.leaves()
  rv = ''
  for word in word_list:
    if word == '(':
      rv += word
    elif word == ')':
      rv = rv[:-1]
      rv += word + ' '
    elif word[0] == "'":
      rv = rv[:-1]
      rv += word + ' '
    elif word == ',':
      rv = rv[:-1]
      rv += word + ' '
    elif word == '.':
      rv = rv[:-1]
      rv += word + ' '
    else:
      rv += word + ' '
  return rv[:-1]

def word_list_join(word_list):
  rv = ''
  for word in word_list:
    if word == '(':
      rv += word
    elif word == ')':
      rv = rv[:-1]
      rv += word + ' '
    elif word[0] == "'":
      rv = rv[:-1]
      rv += word + ' '
    elif word == ',':
      rv = rv[:-1]
      rv += word + ' '
    elif word == '.':
      rv = rv[:-1]
      rv += word + ' '
    else:
      rv += word + ' '
  return rv[:-1]


def immediate_labels(t):
  return map(lambda x: x.label(), t)

def leftmost(t):
  s = t
  while isinstance(s[0], Tree):
    s = s[0]
  return s

def rightmost_pp(t):
  s = t
  while isinstance(s[len(s) - 1], Tree):
    if s[len(s) - 1].label() == 'PP':
      return (s[len(s) - 1], s)
    s = s[len(s) - 1]
  return (None, None)