from nltk.tree import Tree
from SentenceParser import SentenceParser
from treehelpers import *

class SentencesPreprocessor():
  def __init__(self, sentences):
    self.sentences = sentences

  def generate_simple_sentences(self):
    """
    Returns a list of preprocessed sentences that should be easier for making
    questions.
    """
    simple_sentences = []
    for sentence in self.sentences:
      # print sentence
      try:
        t = SentenceParser.parse(sentence)
      except:
        continue
      orig_sentence =  sentence_join(t)
      self.__remove_node_type(t, 'PRN')
      self.__remove_nickname_structures(t)
      simples = self.__extract_simples(t, simple_sentences)
      # for simple in simples:
      #   print sentence_join(simple)
      # if (len(simples) == 0 or (len(simples) == 1 and sentence_join(simples[0]) == orig_sentence)):
      #   print orig_sentence
      #   print t
      simple_sentences.extend(simples)
    return simple_sentences

  def __remove_node_type(self, t, type):
    to_remove = []
    for i in xrange(len(t)):
      if (isinstance(t[i], Tree)):
        if t[i].label() == type:
          if i - 1 >= 0 and t[i - 1].label() == ',':
            to_remove.append(i-1)
            to_remove.append(i)
          else:
            to_remove.append(i)
        else:
          self.__remove_node_type(t[i], type)
    if len(to_remove) == 1:
      del t[to_remove[0]]
    elif len(to_remove) == 2:
      del t[to_remove[0]:to_remove[1]+1]

  def __remove_comma_modifiers(self, t):
    to_remove = []
    for i in xrange(len(t)):
      if (isinstance(t[i], Tree)):
        comma_labels = ['SBAR', 'S', 'PP']
        if t[i].label() in comma_labels:
          if i - 1 >= 0 and t[i - 1].label() == ',':
            to_remove.append(i-1)
            to_remove.append(i)
        else:
          self.__remove_comma_modifiers(t[i])
    if len(to_remove) == 1:
      del t[to_remove[0]]
    elif len(to_remove) == 2:
      del t[to_remove[0]:to_remove[1]+1]

  def __remove_nickname_structures(self, t):
    if len(t) >= 3:
      to_delete = -1
      for i in xrange(len(t) - 2):
        if (isinstance(t[i], Tree)):
          if t[i].label() == "``" or t[i].label() == "''":
            if t[i + 2].label() == "``" or t[i + 2].label() == "''":
              to_delete = i
          else:
            self.__remove_nickname_structures(t[i])
      if to_delete != -1:
        del t[to_delete:to_delete+3]
    else:
      for i in xrange(len(t)):
        if (isinstance(t[i], Tree)):
          self.__remove_nickname_structures(t[i])

  def __get_simples_from_np_vp(self, np, vp, pp=None):
    simples = []
    period = Tree.fromstring('(. .)')
    if pp == None:
      orig = Tree('S', children=[np, vp, period])
    else:
      orig = Tree('S', children=[np, vp, pp, period])
      orig_no_pp = Tree('S', children=[np, vp, period])
    # print sentence_join(orig)
    # print sentence_join(vp)
    # print immediate_labels(vp)
    # print vp
    if ['VP', 'CC', 'VP'] == immediate_labels(vp)[:3]:
      if vp[1][0] == 'and':
        simples.extend(self.__get_simples_from_np_vp(np, vp[0], pp))
        simples.extend(self.__get_simples_from_np_vp(np, vp[2]))
    elif ['VP', ',', 'CC', 'VP'] == immediate_labels(vp)[:4]:
      if vp[2][0] == 'and':
        simples.extend(self.__get_simples_from_np_vp(np, vp[0], pp))
        simples.extend(self.__get_simples_from_np_vp(np, vp[2]))
    else:
      simples.append(orig)
      if pp != None:
        simples.append(orig_no_pp)
    if len(simples) == 0:
      simples.append(orig)
    return simples

  def __clean_nps(self, t, so_far):
    if isinstance(t, str):
      return
    else:
      if t.label() == 'NP':
        no_replace = ['it', 'him', 'her', 'them']
        if len(t) == 1 and t[0].label() == 'PRP' and t[0][0].lower() not in no_replace:
          last = -1
          while len(so_far) + last > -1 and len(so_far[last][0]) == 1 and so_far[last][0][0].label() == 'PRP':
            last -= 1
          if len(so_far) + last > -1:
            t.extend(so_far[last][0])
            del t[0]
            if leftmost(t).label() not in ['NNP', 'NNPS']:
              leftmost(t)[0] = leftmost(t)[0].lower()
        if ',' in immediate_labels(t):
          i = immediate_labels(t).index(',')
          del t[i:]
        if 'SBAR' in immediate_labels(t):
            i = immediate_labels(t).index('SBAR')
            if leftmost(t[i])[0] != 'to' and leftmost(t[i])[0] != 'that':
              del t[i]
      for s in t:
        self.__clean_nps(s, so_far)

  def __extract_simples(self, t, so_far):
    simples = []
    while len(t) == 1:
      t = t[0]
    self.__remove_comma_modifiers(t)
    self.__clean_nps(t, so_far)
    for s in t:
      if s.label() == 'S':
        simples.extend(self.__extract_simples(s, so_far))
    for i in xrange(len(t) - 1):
      if t[i].label() == 'NP' and t[i+1].label() == 'VP':
        simples.extend(self.__get_simples_from_np_vp(t[i], t[i+1]))
    if ['NP', 'VP', '.'] == immediate_labels(t):
      simples.extend(self.__get_simples_from_np_vp(t[0], t[1]))
    elif ['NP', 'ADVP', 'VP', '.'] == immediate_labels(t):
      simples.extend(self.__get_simples_from_np_vp(t[0], t[2]))
    elif ['S', ',', 'NP', 'VP', '.'] == immediate_labels(t):
      del t[0:2]
      simples.extend(self.__get_simples_from_np_vp(t[0], t[1]))
    elif ['PP', ',', 'NP', 'VP', '.'] == immediate_labels(t):
      leftmost(t)[0] = leftmost(t)[0].lower()
      s = t[2]
      s = leftmost(s)
      s[0] = s[0][0].upper() + s[0][1:]
      simples.extend(self.__get_simples_from_np_vp(t[2], t[3], t[0]))
    elif ['SBAR', ',', 'NP', 'VP', '.'] == immediate_labels(t):
      extender = Tree('PP', children=t[0])
      leftmost(extender)[0] = leftmost(extender)[0].lower()
      simples.extend(self.__get_simples_from_np_vp(t[2], t[3], extender))
    # else:
    #   simples.append(t)

    return simples
