from TextParser import TextParser
from SentenceParser import SentenceParser
from SentencesPreprocessor import SentencesPreprocessor
from QuestionGenerator import QuestionGenerator
from treehelpers import *
from nltk.tree import Tree
from nltk.tag.stanford import StanfordNERTagger
import random

def findPatterns(t, label):
  if isinstance(t, str):
    return
  if t.label() == label:
    print label + ": " + " ".join(map(lambda x: x.label(), t)) + " : " + sentence_join(t)
  for s in t:
    findPatterns(s, label)

st = StanfordNERTagger('/Users/renzobautista/Downloads/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz', '/Users/renzobautista/Downloads/stanford-ner-2014-06-16/stanford-ner.jar')

randomset = random.randrange(1, 5)
randomtext = random.randrange(1, 10)
randomset = 4
randomtext = 5
sentences = TextParser('data/set' + str(randomset) + '/a' + str(randomtext) + '.txt').to_sentences()
print 'data/set' + str(randomset) + '/a' + str(randomtext) + '.txt'
# seen = []
# for sentence in sentences:
#   t = SentenceParser.parse(sentence)
#   while len(t) == 1:
#     t = t[0]
#   labels = immediate_labels(t)
#   if labels not in seen:
#     seen.append(labels)
#     print labels
#     print sentence_join(t)
#   findPatterns(t, 'NP')
#   findPatterns(t, 'VP')

preprocessor = SentencesPreprocessor(sentences)
simple_sentences = preprocessor.generate_simple_sentences()

generated = []
for s in simple_sentences:
  # print preprocessor.sentence_join(s)
  # print map(lambda x: x.label(), s)
  # print map(lambda x: x.label(), s[1])
  for question in QuestionGenerator(s).create():
    if len(question.split()) > 5 and len(question.split()) < 20:
      if question not in generated:
        print question
        generated.append(question)
    # continue

# for sentence in sentences:
#   sentence_tree = SentenceParser.parse(sentence)
#   t = Tree.fromstring(sentence_tree)
#   while len(t) == 1:
#     t = t[0]
#   print len(t)

# PRETTY GOOD ESTIMATION FOR IS NP1 NP2? QUESTIONS
# for t in simple_sentences:
#   s_tree = t
#   while len(s_tree) == 1:
#     s_tree = s_tree[0]
#   sections = []
#   for subtree in s_tree:
#     label = subtree.label()
#     # section = ' '.join(subtree.leaves())
#     section = subtree.leaves()
#     sections.append((label, section))
#   if (sections[0][0] == 'NP' and sections[1][0] == 'VP' and len(sections) == 3):
#     if sections[1][1][0] == 'is':
#       question = "Is " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question
#     elif sections[1][1][0] == 'are':
#       question = "Are " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question
#     elif sections[1][1][0] == 'was':
#       question = "Was " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question
#     elif sections[1][1][0] == 'were':
#       question = "Were " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question
#     elif sections[1][1][0] == 'will':
#       question = "Will " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question
#     elif sections[1][1][0] == 'can':
#       question = "Can " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question
#     elif sections[1][1][0] == 'do':
#       question = "Do " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question
#     elif sections[1][1][0] == 'does':
#       question = "Does " + ' '.join(sections[0][1]) + ' ' + ' '.join(sections[1][1][1:]) + '?'
#       print question

# # Let's try to do some NER now
# def clause_before_and(word_list):
#   if 'and' in word_list:
#     end_index = word_list.index('and')
#     if word_list[end_index - 1] == ',':
#       end_index -= 1
#     return word_list[0:end_index]
#   else:
#     return word_list

# def clean_section(word_list):
#   for i in xrange(len(word_list)):
#     if word_list[i] == '-LRB-':
#       word_list[i] = '('
#     if word_list[i] == '-RRB-':
#       word_list[i] = ')'
#   return word_list

# def sentence_join(word_list):
#   rv = ''
#   for word in word_list:
#     if word == '(':
#       rv += word
#     elif word == ')':
#       rv = rv[:-1]
#       rv += word + ' '
#     elif word[0] == "'":
#       rv = rv[:-1]
#       rv += word + ' '
#     elif word == ',':
#       rv = rv[:-1]
#       rv += word + ' '
#     else:
#       rv += word + ' '
#   return rv[:-1]

# def is_personal_pronoun(word):
#   pronoun_list = ['he', 'she', 'they', 'i', 'you', 'we']
#   return word.lower() in pronoun_list

# def is_valid_np(word_list):
#   is_valid = True
#   if len(word_list) == 1 and word_list[0] == 'It':
#     is_valid = False
#   if len(word_list) <= 3 and word_list[0] == 'The':
#     is_valid = False
#   return is_valid

# for t in simple_sentences:
#   question = ""
#   s_tree = t
#   while len(s_tree) == 1:
#     s_tree = s_tree[0]
#   sections = []
#   for subtree in s_tree:
#     label = subtree.label()
#     # section = ' '.join(subtree.leaves())
#     section = subtree.leaves()
#     section = clean_section(section)
#     sections.append((label, section))
#   if (sections[0][0] == 'NP' and sections[1][0] == 'VP' and len(sections) == 3 and is_valid_np(sections[0][1]) and len(sections[0][1]) + len(sections[1][1]) <= 30):
#     wh_word = "What"
#     ner_tags = st.tag(sections[0][1])
#     if (is_personal_pronoun(sections[0][1][0]) and len(sections[0][1]) == 1):
#       wh_word = "Who"
#     for i in xrange(min(3, len(ner_tags))):
#       if ner_tags[i][1] == u'PERSON':
#         wh_word = "Who"
#         break
#     question = wh_word + " " + sections[1][1][0] + " " + sentence_join(sections[1][1][1:]) + '?'
#     print question


# PREPROCESSING SENTENCES
# def remove_node_type(t, type):
#   for i in xrange(len(t)):
#     if (isinstance(t[i], Tree)):
#       if t[i].label() == type:
#         if i - 1 >= 0 and t[i - 1].label() == ',':
#           del t[i-1:i+1]
#         else:
#           del t[i]
#       else:
#         remove_node_type(t[i], type)

# def remove_nickname_structures(t):
#   if len(t) >= 3:
#     to_delete = -1
#     for i in xrange(len(t) - 2):
#       if (isinstance(t[i], Tree)):
#         if t[i].label() == "``" or t[i].label() == "''":
#           if t[i + 2].label() == "``" or t[i + 2].label() == "''":
#             to_delete = i
#         else:
#           remove_nickname_structures(t[i])
#     if to_delete != -1:
#       del t[to_delete:to_delete+3]
#   else:
#     for i in xrange(len(t)):
#       if (isinstance(t[i], Tree)):
#         remove_nickname_structures(t[i])

# def get_simples_from_np_vp(np, vp, pp=None):
#   simples = []
#   period = Tree.fromstring('(. .)')
#   if pp == None:
#     orig = Tree('S', children=[np, vp, period])
#   else:
#     orig = Tree('S', children=[np, vp, pp, period])
#   if ['VP', 'CC', 'VP'] == map(lambda x: x.label(), vp):
#     if vp[1][0] == 'and':
#       if pp:
#         simples.append(Tree('S', children=[np, vp[0], pp, period]))
#       else:
#         simples.append(Tree('S', children=[np, vp[0], period]))
#       simples.append(Tree('S', children=[np, vp[2], period]))
#   if len(simples) == 0:
#     simples.append(orig)
#   return simples

# def extract_simples(t):
#   simples = []
#   while len(t) == 1:
#     t = t[0]
#   remove_node_type(t, 'SBAR')
#   if len(t) == 3:
#     if ['NP', 'VP', '.'] == map(lambda x: x.label(), t):
#       simples.extend(get_simples_from_np_vp(t[0], t[1]))
#   if len(t) == 5:
#     if ['S', ',', 'NP', 'VP', '.'] == map(lambda x: x.label(), t):
#       del t[0:2]
#       simples.extend(get_simples_from_np_vp(t[0], t[1]))
#     elif ['PP', ',', 'NP', 'VP', '.'] == map(lambda x: x.label(), t):
#       t[0][0][0] = t[0][0][0].lower()
#       s = t[2]
#       while isinstance(s[0], Tree):
#         s = s[0]
#       s[0] = s[0][0].upper() + s[0][1:]
#       simples.extend(get_simples_from_np_vp(t[2], t[3], t[0]))
#   return simples

# sentence_tree = SentenceParser.parse(sentences[6])
# t = Tree.fromstring(sentence_tree)
# print t
# remove_node_type(t, 'PRN')
# remove_nickname_structures(t)
# simples = extract_simples(t)
# for simple in simples:
#   print simple



# PRINT ALL PHRASE STRUCTURES IN A SENTENCE
# def phrase_from_tree(t):
#   return ' '.join(t.leaves())

# def get_immediate_phrase_structure(t):
#   if (isinstance(t, Tree)):
#     structure = []
#     if len(t.leaves()) > 1:
#       for subtree in t:
#         structure.append((subtree.label(), phrase_from_tree(subtree)))
#     return structure
#   else:
#     return []

# def get_all_phrase_structures(t):
#   structures = [get_immediate_phrase_structure(t)]
#   for subtree in t:
#     if (isinstance(subtree, Tree)):
#       substructures = get_all_phrase_structures(subtree)
#       for substructure in substructures:
#         if len(substructure) > 0:
#           structures.append(substructure)
#   return structures

# sentence_tree = SentenceParser.parse(sentences[0])
# t = Tree.fromstring(sentence_tree)
# print t
# for structure in get_all_phrase_structures(t):
#   print structure

























