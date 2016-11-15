from treehelpers import *
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

class QuestionGenerator():

  def __init__(self, sentence):
    self.sentence = sentence
    self.lemmatizer = WordNetLemmatizer()

  def create(self):
    t = self.sentence
    questions = []
    if ['NP', 'VP', 'PP', '.'] == immediate_labels(t):
      questions.append(self.__create_wh_question(t))

    np1_np2_question = self.__create_np1_np2_question(t)
    if np1_np2_question:
      questions.append(np1_np2_question)

    # if len(questions) == 0:
    #   print ""
    #   print sentence_join(t)
    #   print t
    #   print ""

    return list(set(questions))

  def __create_np1_np2_question(self, t):
    sections = []
    for s in t:
      label = s.label()
      section = s.leaves()
      sections.append((label, section))
    question = None
    np_phrase = word_list_join(sections[0][1])
    vp_phrase = word_list_join(sections[1][1][1:])
    if vp_phrase.startswith('also '):
      vp_phrase = vp_phrase[5:]
    if leftmost(t[0]).label() != 'NNP':
      np_phrase = np_phrase[0].lower() + np_phrase[1:]
    if (sections[0][0] == 'NP' and sections[1][0] == 'VP'):
      if sections[1][1][0] == 'is':
        question = "Is " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'are':
        question = "Are " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'was':
        question = "Was " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'were':
        question = "Were " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'will':
        question = "Will " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'can':
        question = "Can " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'do':
        question = "Do " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'does':
        question = "Does " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'has' and t[1][1].label() in ['VP', 'ADVP']:
        question = "Has " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'had' and t[1][1].label() in ['VP', 'ADVP']:
        question = "Had " + np_phrase + ' ' + vp_phrase + '?'
      elif sections[1][1][0] == 'have' and t[1][1].label() in ['VP', 'ADVP']:
        question = "Have " + np_phrase + ' ' + vp_phrase + '?'
      else:
        verb = leftmost(t[1])
        do_word = None
        if verb.label() == 'VBD':
          do_word = 'Did '
        elif verb.label() == 'VBZ':
          do_word = 'Does '
        elif verb.label() == 'VBP':
          d_word = 'Do '
        if do_word:
          verb = self.lemmatizer.lemmatize(t[1].leaves()[0], 'v')
          question = do_word + np_phrase + ' ' + verb + ' ' + word_list_join(t[1].leaves()[1:]) + '?'

    return question

  def __create_wh_question(self, t):
    wh_word = self.__get_wh_word(t[2])
    d_word = 'do'

    if leftmost(t[1]).label() == 'VBD': # past
      d_word = 'did'
    elif leftmost(t[1]).label() == 'VBZ': # present third person
      d_word = 'does'
    elif leftmost(t[1]).label() == 'VBP': # present first person
      d_word = 'do'
    np_phrase = sentence_join(t[0])
    if leftmost(t[0]).label() != 'NNP':
      np_phrase = np_phrase[0].lower() + np_phrase[1:]
    verb = self.lemmatizer.lemmatize(t[1].leaves()[0], 'v')
    vp_rest = word_list_join(t[1].leaves()[1:])

    sentence = ''
    special_verbs = ['will', 'be', 'can', 'could', 'would', 'have', 'do']
    if verb in special_verbs:
      sentence = ' '.join([wh_word, t[1].leaves()[0], np_phrase, vp_rest]) + '?'
    else:
      sentence = ' '.join([wh_word, d_word, np_phrase, verb, vp_rest]) + '?'

    # if abs(len(sentence.split()) - 9) > 4:
    #   sentence = ''
    return sentence

  def __get_wh_word(self, t):
    wh_word = 'Where'
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    years = map(lambda x: str(x), range(1900, 2017))
    trigger_words = ['after', 'before', 'ago', 'during', 'age']
    for word in t.leaves():
      if word in months:
        wh_word = 'When'
      elif word in years:
        wh_word = 'When'
      elif word in trigger_words:
        wh_word = 'When'
    if wh_word == 'When' and t.leaves()[0] == 'since':
      wh_word = 'Since when'
    return wh_word
