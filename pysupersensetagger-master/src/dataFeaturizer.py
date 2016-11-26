'''
Created on Jun 2, 2013

@author: Nathan Schneider (nschneid)
'''
from __future__ import print_function, division

import os, sys, codecs

from labeledSentence import LabeledSentence
import morph

USTRINGS = {}
def uintern(unicode_string):
    '''Simulate built-in intern(), but in a way that works for unicode strings.'''
    return USTRINGS.setdefault(unicode_string,unicode_string)

class DataSet(object):
    def __init__(self, f):
        self._file = f
    def __iter__(self):
        return 

class SupersenseDataSet(DataSet):
    def __init__(self, path, labels, legacy0, keep_in_memory=True, autoreset=True):
        '''
        'labels' should contain all valid tags; if a tag is encountered in the data 
        but is not included in 'labels', it will be replaced with 'O'.
        'labels' can also be None to mean all labels are acceptable, but this is 
        not recommended as it will remove an opportunity to catch preprocessing errors.
        '''
        self._path = path
        self._labels = labels
        self._cache = [] if keep_in_memory else None
        self._legacy0 = legacy0
        self._autoreset = autoreset
        self.open_file()
    
    def close_file(self):
        self._f.close()
    
    def open_file(self):
        self._f = open(self._path)  # using codecs.open() was screwing up line buffering
    
    def reset(self):
        '''Stop reading more input instances, and prepare to start at the beginning.'''
        if self._cache is None:
            self._f.seek(0)
        else:
            self.close_file()
        self._reset = True  # TODO: not sure about this mechanism for short-circuiting existing iterators
    
    def _read_nonblank_line(self, ln, sent):
        '''Tab-separated format:
        word   pos   tag   sentId
        tag and sentId are optional.
        '''
        parts = ln[:-1].split('\t')[:4]
        if len(parts)==4:
            token, pos, tag, sentId = parts
            sent.sentId = sentId
        elif len(parts)==3:
            token, pos, tag = parts
            if not tag.strip():
                tag = None
        else:
            token, pos = parts
            tag = None
        
        
        if tag is not None:
            if self._labels is None:
                pass
            elif tag=='0' and self._legacy0:
                assert 'O' in self._labels,self._labels
                tag = 'O'
            elif tag not in self._labels:
                tag = 'O'
            tag = uintern(unicode(tag))
            
        pos = uintern(unicode(pos))
        stemS = uintern(unicode(morph.stem(token,pos)))
        sent.addToken(token=token, stem=stemS, pos=pos, goldTag=tag)
    
    def __iter__(self):
        '''
        Load the BIO tagged supersense data from Semcor, as provided in 
        the SuperSenseTagger release (SEM_07.BI).
        We also use their POS labels, which presumably were what their 
        paper used.
        One difference is that this method expects the data to be converted 
        into a 3-column format with an extra newline between each sentence 
        (as in CoNLL data), which can be created from the SST data with 
        a short perl script. 
        '''
        self._reset = False
        if self._f.closed:
            assert self._cache
            for sent in self._cache:
                yield sent
        else:
            sent = LabeledSentence()
            while True:                 # instead of for loop, due to buffering issue
                ln = self._f.readline().decode('utf-8') # with stdin (this will ensure one line is processed at a time)
                if not ln.strip():
                    if len(sent)>0:
                        if self._cache is not None:
                            self._cache.append(sent)
                        yield sent
                        if self._reset:
                            raise StopIteration()
                        sent = LabeledSentence()
                    if not ln:  # end of input
                        break
                    continue
                
                self._read_nonblank_line(ln, sent)
                
            if len(sent)>0:
                if self._cache is not None:
                    self._cache.append(sent)
                yield sent
                
            if self._autoreset:
                self.reset()

class SupersenseTrainSet(SupersenseDataSet):
    '''Dataset in 8- or 9-column format with gold tags''' 
    
    def _read_nonblank_line(self, ln, sent):
        '''Tab-separated format:
        offset   word   lemma   POS   tag   parent   strength   label   sentId
        lemma will (for now) be ignored in favor of the automatic stemmer.
        label may be the empty string; sentId is optional.
        '''
        parts = ln[:-1].split('\t')
        if len(parts)==9:
            offset, token, _, pos, tag, parent, strength, label, sentId = parts
            sent.sentId = sentId
        else:
            offset, token, _, pos, tag, parent, strength, label = parts
        
        offset = int(offset)
        parent = int(parent)
        assert len(sent)+1==offset
        assert parent<offset
        
        
        if tag is not None:
            if self._labels is None:
                pass
            elif tag=='0' and self._legacy0:
                assert 'O' in self._labels,self._labels
                tag = 'O'
            elif tag not in self._labels:
                tag = 'O'
            tag = uintern(unicode(tag))
            
        pos = uintern(unicode(pos))
        stemS = uintern(unicode(morph.stem(token,pos)))
        sent.addToken(token=token, stem=stemS, pos=pos, goldTag=tag, 
                      goldparent=int(parent), goldstrength=uintern(unicode(strength)), 
                      goldlabel=uintern(unicode(label)))



class SupersenseFeaturizer(object):
    
    def __init__(self, extractor, dataset, indexes, cache_features=True, domain_prefixes=None):
        self._extractor = extractor
        self._data = dataset
        self._featureIndexes = indexes
        self._features = [] if cache_features else None
        # TODO: For now, try caching just the lifted 0-order features.
        self._domain_prefixes = domain_prefixes
    
    def __iter__(self):
        for j,sent in enumerate(self._data):
            if self._features is None or j>=len(self._features):  # not yet in cache
                lexiconCandidatesThisSent = self._extractor.extractLexiconCandidates(sent)
                supersenseCandidatesThisSent = self._extractor.extractWNSupersenseCandidates(sent)
                
                o0FeatsEachToken = []
                
                for i in range(len(sent)):
                    # zero-order features (lifted)
                    o0FeatureMap = self._extractor.extractFeatureValues(sent, i, 
                                                                        usePredictedLabels=False, 
                                                                        orders={0}, 
                                                                        indexer=self._featureIndexes, 
                                                                        candidatesThisSentence=(lexiconCandidatesThisSent,supersenseCandidatesThisSent))
                    
                    if not o0FeatureMap:
                        raise Exception('No 0-order features found for this token')
                    
                    # domain-specific features
                    baseFeatures = list(o0FeatureMap.named_items())
                    for pre in self._domain_prefixes or ():
                        if sent.sentId.startswith(pre):
                            for f,v in baseFeatures:
                                o0FeatureMap[(pre,f)] = v
                    
                    o0FeatsEachToken.append(o0FeatureMap)
                    
                if self._features is not None:
                    assert len(self._features)==j
                    self._features.append(o0FeatsEachToken)
                
                yield sent,o0FeatsEachToken
            else:
                yield sent,self._features[j]
    
    def enable_caching(self):
        if self._features is None:
            self._features = []
    
    def reset(self):
        self._data.reset()

    def write_feature_vocab(self, outF, numbered=True):
        '''Writes the percept vocabulary to a file, optionally with percept indices.'''
        n = 0
        for i,pname in self._featureIndexes.items():
            n += 1
            if numbered:
                outF.write(str(i)+'\t')
            print(pname, file=outF)
        return 'Wrote names for {} features'.format(n)

    def write_features(self, outF, format='numeric'):
        '''Writes this dataset to a file in terms of its extracted observation features. 
        For each token, the word, gold tag, and active zero-order percepts.'''
        if format!='numeric': raise NotImplementedError('Unsupported format: '+format)
        nS = nW = 0
        for sent,o0FeatsEachToken in self:
            nS += 1
            for w,o0Feats in zip(sent,o0FeatsEachToken):
                nW += 1
                outF.write(w.token+'\t'+w.gold+'\t')
                outF.write(' '.join('{}:{}'.format(*itm) for itm in sorted(o0Feats.items())))
                outF.write('\n')
            outF.write('\n')
        return 'Wrote features for {} words, {} sentences'.format(nW, nS)
