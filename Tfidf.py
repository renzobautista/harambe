import nltk
import string

from sklearn.feature_extraction.text import TfidfVectorizer


def sentence_similarity(sentence1, sentence2):
    tfidf_vec = TfidfVectorizer(min_df = 1)
    tfidf_mat = tfidf_vec.fit_transform([sentence1, sentence2])
    return (tfidf_mat * tfidf_mat.T).A[0][1]


if __name__ == '__main__':
    print sentence_similarity('Harambe is a dog.', 'Is harambe a dog?')
    print sentence_similarity('Harambe is a dog.', 'Is harambe a dog?')
    print sentence_similarity('Harambe is a dog.', 'We get it you')
    print sentence_similarity('Shots fired.', 'How are you?')
    print sentence_similarity('How is your day?', 'I\'m fine')
    print sentence_similarity('How is your day?', 'My day is alright')
    print sentence_similarity('Who is the president?', 'The president is Obama')
    print sentence_similarity('Have you eaten?', 'I have eaten.')
