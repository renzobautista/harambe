from treehelpers import *
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree
import nltk

class QuestionGenerator():

  def __init__(self, sentence):
    self.sentence = sentence
    self.lemmatizer = WordNetLemmatizer()

  def create(self):
    t = self.sentence
    questions = []
    if ['NP', 'VP', 'PP', '.'] == immediate_labels(t):
      question = self.__create_wh_question(t)
      if question is not None:
        questions.append(question)
    if ['NP', 'VP', '.'] == immediate_labels(t):
      s = t.copy(deep=True)
      (answer, parent) = first_right_np_pp(s[1])
      if answer is not None:
        if answer.label() == 'NP':
          answer_copy = answer.copy(deep=True)
          del parent[-1]
          new_sentence = Tree('S', children=[s[0], s[1], answer_copy, s[2]])
          question = self.__get_who_what_question(new_sentence)
          if question is not None:
            questions.append(question)
        elif answer.label() == 'PP':
          answer_copy = answer.copy(deep=True)
          del parent[-1]
          new_sentence = Tree('S', children=[s[0], s[1], answer_copy, s[2]])
          question = self.__create_wh_question(new_sentence)
          if question is not None:
            questions.append(question)

    np1_np2_question = self.__create_np1_np2_question(t)
    if np1_np2_question:
      questions.append(np1_np2_question)

    # if len(questions) == 0:
    #   print ""
    #   print sentence_join(t)
    #   print t
    #   print ""

    nt_filtered_questions = []
    for question in questions:
      nt_question = question.replace(" n't", "")
      nt_filtered_questions.append(nt_question)

    return list(set(nt_filtered_questions))

  def __create_np1_np2_question(self, t):
    sections = []
    if len(t) < 3 or (t[0].label() != 'NP' or t[1].label() != 'VP'):
      return None
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
        question = ("Is " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'are':
        question = ("Are " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'was':
        question = ("Was " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'were':
        question = ("Were " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'will':
        question = ("Will " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'can':
        question = ("Can " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'do':
        question = ("Do " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'does':
        question = ("Does " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'has' and len(t[1]) > 1 and t[1][1].label() in ['VP', 'ADVP']:
        question = ("Has " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'had' and len(t[1]) > 1 and t[1][1].label() in ['VP', 'ADVP']:
        question = ("Has " + np_phrase + ' ' + vp_phrase).strip() + '?'
      elif sections[1][1][0] == 'have' and len(t[1]) > 1 and t[1][1].label() in ['VP', 'ADVP']:
        question = ("Have " + np_phrase + ' ' + vp_phrase).strip() + '?'
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
          question = (do_word + np_phrase + ' ' + verb + ' ' + word_list_join(t[1].leaves()[1:])).strip() + '?'

    return question

  def __create_wh_question(self, t):
    wh_word = self.__get_wh_word(t[2])
    if wh_word == None:
      return None
    d_word = 'do'

    if isinstance(t[1][0], Tree) and t[1][0].label() == 'ADVP':
      del t[1][0]
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
      sentence = ' '.join([wh_word, t[1].leaves()[0], np_phrase, vp_rest]).strip() + '?'
    else:
      sentence = ' '.join([wh_word, d_word, np_phrase, verb, vp_rest]).strip() + '?'

    # if abs(len(sentence.split()) - 9) > 4:
    #   sentence = ''
    return sentence

  def __get_who_what_question(self, t):
    wh_word = self.__get_who_or_what_from_np(t[2])
    if wh_word == None:
      return None
    d_word = 'do'

    if isinstance(t[1][0], Tree) and t[1][0].label() == 'ADVP':
      del t[1][0]
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
      sentence = ' '.join([wh_word, t[1].leaves()[0], np_phrase, vp_rest]).strip() + '?'
    else:
      sentence = ' '.join([wh_word, d_word, np_phrase, verb, vp_rest]).strip() + '?'
    return sentence

  def __get_wh_word(self, t):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    years = map(lambda x: str(x), range(1900, 2017))
    when_trigger_words = ['after', 'before', 'ago', 'during', 'age', 'day', 'hour', 'minute', 'when']
    where_trigger_words = ['in', 'at', 'behind', 'above', 'next to', 'under', 'inside', 'to', 'below', 'outside', 'front', 'across from', 'right', 'left', 'back']
    why_trigger_words = ['because', 'due to']
    sentence = sentence_join(t)
    for word in why_trigger_words:
      if sentence.startswith(word):
        return 'Why'
    for word in months:
      if word in sentence:
        return 'When'
    for word in years:
      if word in sentence:
        return 'When'
    for word in when_trigger_words:
      if word in sentence:
        return 'When'
    for word in where_trigger_words:
      if word in sentence:
        return 'Where'
    return None

  def __get_who_or_what_from_np(self, t):
    chunks = nltk.ne_chunk(t.pos())
    if isinstance(chunks[0], Tree) and chunks[0].label() == 'PERSON':
      return 'Who'
    else:
      return 'What'
