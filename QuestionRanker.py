from SentenceParser import SentenceParser
from sklearn.naive_bayes import GaussianNB
from nltk.tree import Tree
from treehelpers import *
import pickle

def count_pps(t):
  count = 0
  if isinstance(t, Tree):
    if t.label() == 'PP':
      return 1
    else:
      for s in t:
        count += count_pps(s)
      return count
  else:
    return count


def count_nps(t):
  count = 0
  if isinstance(t, Tree):
    if t.label() == 'NP':
      return 1
    else:
      for s in t:
        count += count_nps(s)
      return count
  else:
    return count

def train():
  # number of words
  # number of PRP
  # number of NP
  # number of PP
  # number of nouns
  file = open('training.txt')
  file_content = file.read()
  feature_data = []
  target_data = []
  for line in file_content.splitlines():
      question_is_good = line[0] == 'G'
      if question_is_good:
        target_data.append(1)
      else:
        target_data.append(0)

      question = line[1:]
      t = SentenceParser.parse(question)
      pos = tuple(map(lambda w: w[1], t.pos()))

      word_length = len(sentence_join(t).split())
      num_pronouns = 0
      for p in pos:
        if p == 'PRP':
          num_pronouns += 1
      num_nps = count_nps(t)
      num_pps = count_pps(t)
      num_nouns = 0
      for p in pos:
        if p.startswith('NN'):
          num_nouns += 1
      feature_data.append([word_length, num_pronouns, num_nps, num_pps, num_nouns])
  gnb = GaussianNB()
  return gnb.fit(feature_data, target_data)


class QuestionRanker():
  nb_classifier = pickle.load(open('nb.pickle', 'rb'))

  def __init__(self, question):
    self.question = question

  def score(self):
    if self.__has_illegal_first_five_words():
      return 0
    if self.question.startswith("Where had") or self.question.startswith("When had"):
      return 0

    return self.__vocab_score()

  def __vocab_score(self):
    try:
      t = SentenceParser.parse(self.question)
    except:
      return 0
    pos = tuple(map(lambda w: w[1], t.pos()))

    word_length = len(sentence_join(t).split())
    num_pronouns = 0
    for p in pos:
      if p == 'PRP':
        num_pronouns += 1
    num_nps = count_nps(t)
    num_pps = count_pps(t)
    num_nouns = 0
    for p in pos:
      if p.startswith('NN'):
        num_nouns += 1
    feature_vector = [[word_length, num_pronouns, num_nps, num_pps, num_nouns]]
    return QuestionRanker.nb_classifier.predict_proba(feature_vector)[0][1]

  def __has_illegal_first_five_words(self):
    disallowed_first_five_words = ['it', 'its', 'he', 'his', 'she', 'her', 'they', 'their', 'we', 'our', 'I', 'my', 'you', 'your', 'the', 'this', 'that', 'those', 'these']
    first_five_words = self.question.split()[:5]    
    for word in disallowed_first_five_words:
      if word in first_five_words:
        return True
    return False
