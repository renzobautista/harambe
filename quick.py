from SentenceParser import SentenceParser

tmp = open("pysupersensetagger-master/example1", "w")
s = "On November 12, 2012, Stevens was arrested on investigation of assault following an altercation that left Solo injured."
p = SentenceParser.parse(s).pos()
for i in xrange(len(p)):
  (p1, p2) = p[i]
  tmp.write(p1 + "\t" + p2 + "\n")