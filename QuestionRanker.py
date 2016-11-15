

class QuestionRanker():

  def __init__(self, question):
    self.question = question

  def score(self):
    if len(self.question.split()) < 5 or len(self.question.split()) > 20:
      return 0
    if self.__has_illegal_first_five_words():
      return 0

    return 1

  def __has_illegal_first_five_words(self):
    disallowed_first_five_words = ['it', 'its', 'he', 'his', 'she', 'her', 'they', 'their', 'we', 'our', 'I', 'my', 'you', 'your', 'the']
    first_five_words = self.question.split()[:5]    
    for word in disallowed_first_five_words:
      if word in first_five_words:
        return True
    return False
