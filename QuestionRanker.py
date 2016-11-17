from SentenceParser import SentenceParser

def train():
  file = open('training.txt')
  file_content = file.read()
  vocab = {}
  good_vocab = {}
  bad_vocab = {}
  all_vocabs = []
  for line in file_content.splitlines():
      question_is_good = line[0] == 'G'
      question = line[2:]

      t = SentenceParser.parse(question)
      labels = tuple(map(lambda w: w[1], t.pos()))

      if labels not in all_vocabs:
        all_vocabs.append(labels)

      if question_is_good:
        if labels in good_vocab:
          good_vocab[labels] += 1
        else:
          good_vocab[labels] = 1
        if labels not in bad_vocab:
          bad_vocab[labels] = 0
      else:
        if labels in bad_vocab:
          bad_vocab[labels] += 1
        else:
          bad_vocab[labels] = 1
        if labels not in good_vocab:
          good_vocab[labels] = 0

  for labels in all_vocabs:
    p_good = float(good_vocab[labels])/(good_vocab[labels] + bad_vocab[labels])
    vocab[labels] = p_good
  return vocab

class QuestionRanker():
  vocab = train()

  def __init__(self, question):
    self.question = question

  def score(self):
    if len(self.question.split()) <= 5 or len(self.question.split()) >= 20:
      return 0
    if self.__has_illegal_first_five_words():
      return 0

    return self.__vocab_score()

  def __vocab_score(self):
    try:
      t = SentenceParser.parse(self.question)
    except:
      return 1
    labels = tuple(map(lambda w: w[1], t.pos()))
    if labels in QuestionRanker.vocab:
      score = QuestionRanker.vocab[labels]
    else:
      score = 1
    return score


  def __has_illegal_first_five_words(self):
    disallowed_first_five_words = ['it', 'its', 'he', 'his', 'she', 'her', 'they', 'their', 'we', 'our', 'I', 'my', 'you', 'your', 'the', 'this', 'that', 'those', 'these']
    first_five_words = self.question.split()[:5]    
    for word in disallowed_first_five_words:
      if word in first_five_words:
        return True
    return False
