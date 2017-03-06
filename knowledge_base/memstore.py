# types of all possible perspectives on a ternary corpus
from knowledge_base.lexicon import Lexicon
from knowledge_base.tensor import Tensor
import os, pickle, gzip
from math import log
from _collections import defaultdict

PERSP_TYPES = ['LAxLIRA','LIxLARA','RAxLALI','LIRAxLA','LARAxLI','LALIxRA',\
'LAxLIRA_COMPRESSED','LIxLARA_COMPRESSED','RAxLALI_COMPRESSED',\
'LIRAxLA_COMPRESSED','LARAxLI_COMPRESSED','LALIxRA_COMPRESSED']

# pivot dimensions to 'lock' when computing a perspective matricisation
PERSP2PIVDIM = {
  'LAxLIRA' : 0,
  'LIxLARA' : 1,
  'RAxLALI' : 2,
  'LIRAxLA' : (1,2),
  'LARAxLI' : (0,2),
  'LALIxRA' : (0,1)
}

class MemStore:

    def __init__(self,trace=False):
        self.lexicon = Lexicon()
        self.sources = Tensor(rank=4)
        self.corpus = Tensor(rank=3)
        self.perspectives = dict([(x,Tensor(rank=2)) for x in PERSP_TYPES])
        self.types = {}
        self.synonyms = {}
        self.trace = trace

    def convert(self,statement):
        """
        Backwards compatibility function for converting between integer and
        string representations of statements.
        """

        return tuple([self.lexicon[x] for x in statement])

    def incorporate(self, closenesses):
        """
        Imports the statements into the store, processing all files with the
        specified extension ext in the path location. Lexicon and sources
        structures are updated (not overwritten) in the process.
        
            Args:
                closenesses: The calculcated Closeness objects from extract_step.
        """
        
        expressions = []
        
        # first pass: update lexicon with terms
        for paragraph_closeness in closenesses:
            for closeness in paragraph_closeness:
                expressions += [closeness.term, "close to", closeness.close_to, closeness.paragraph_id]
        self.lexicon.update(expressions)
        
        for paragraph_closeness in closenesses:
            for closeness in paragraph_closeness:
                #line = [closeness.term, "close to", closeness.close_to, closeness.paragraph_id]
                
                key = (closeness.term, "close to", closeness.close_to, closeness.paragraph_id)
                ### DOES NOT WORK BECAUSE I DONT USE THE LEX2INT STUFF
                ### RETURNS INT
                #key = tuple([self.lexicon[x] for x in line]) ### square brackets calls __getitem__
                #print("MY SYSTEM, KEY", key)
                print("MY SYSTEM KEY", key)
                self.sources[key] = closeness.closeness

    def dump(self,filename):
        # straightforward (but somehow slow) (de)serialisation using cPickle
        pickle.dump(self,open(filename,'w'))

    def load(self,filename):
        # straightforward (but somehow slow) (de)serialisation using cPickle
        self = pickle(open(filename,'r'))

    def exp(self,path,compress=True,core_only=True):
        # exporting the whole store as tab-separated value files to a directory
        # (gzip compression is used by default)
        # note that only lexicon, sources and corpus structures are exported, any
        # possibly precomputed corpus perspectives have to be re-created!
        # also, integer indices are used - for lexicalised (human readable) export
        # of sources and corpus, use exportSources() and exportCorpus() functions
        # setting the filenames
        lex_fn = os.path.join(path,'lexicon.tsv')
        src_fn = os.path.join(path,'sources.tsv')
        crp_fn = os.path.join(path,'corpus.tsv')
        if compress:
            lex_fn += '.gz'
            src_fn += '.gz'
            crp_fn += '.gz'
        openner, sig = open, 'w'
        if compress:
            openner, sig = gzip.open, 'w'
        lex_f = openner(lex_fn,sig)
        src_f = openner(src_fn,sig)
        crp_f = openner(crp_fn,sig)
        self.lexicon.to_file(lex_f)
        self.sources.to_file(src_f)
        self.corpus.to_file(crp_f)
        lex_f.close()
        src_f.close()
        crp_f.close()

    def imp(self,path,compress=True):
        # importing the whole store as tab-separated value files from a directory
        # effectively an inverse of the exp() function
        lex_fn = os.path.join(path,'lexicon.tsv')
        src_fn = os.path.join(path,'sources.tsv')
        crp_fn = os.path.join(path,'corpus.tsv')
        if compress:
            lex_fn += '.gz'
            src_fn += '.gz'
            crp_fn += '.gz'
        openner, sig = open, 'r'
        if compress:
            openner, sig = gzip.open, 'rb'
        lex_f = openner(lex_fn,sig)
        src_f = openner(src_fn,sig)
        crp_f = openner(crp_fn,sig)
        self.lexicon.from_file(lex_f)
        self.sources.from_file(src_f)
        self.corpus.from_file(crp_f)
        lex_f.close()
        src_f.close()
        crp_f.close()

    def computeCorpus(self):
        # number of all triples
        N = 0
        # x -> number of independednt occurences in the store
        indep_freq = defaultdict(int)
        
        # (x,y) -> number of joint occurences in the store
        joint_freq = defaultdict(int)
        
        # (s,p,o) -> number of occurences
        tripl_freq = defaultdict(int)
        
        # (s,p,o) -> (provenance, relevance)
        spo2pr = {}
        
        # going through all the statements in the sources
        for s,p,o,d in list(self.sources.keys()):
            N += 1
            
            ### refactored to use defaultdict
            indep_freq[s] += 1
            indep_freq[o] += 1
            joint_freq[(s,o)] += 1
            tripl_freq[(s,p,o)] += 1
            if (s,p,o) not in spo2pr:
                spo2pr[(s,p,o)] = []
            spo2pr[(s,p,o)].append((d,self.sources[(s,p,o,d)]))
        # going only through the unique triples now regardless of their provenance
        for s,p,o in spo2pr:
            # a list of relevances of particular statement sources
            src_rels = [x[1] for x in spo2pr[(s,p,o)]]
            ### src rels has sometimes more than 1 value
            
            # absolute frequency of the triple times it's mutual information score
            joint = joint_freq[(s,o)]
            if (o,s) in joint_freq:
                ### o and s are terms
                joint += joint_freq[(o,s)]
            # frequency times mutual information score
            fMI = 0.0
            try:
                fMI = \
                tripl_freq[(s,p,o)]*log(float(N*joint)/(indep_freq[s]*indep_freq[o]),2)
            except ValueError:
                continue
            # setting the corpus tensor value
            self.corpus[(s,p,o)] = fMI*(float(sum(src_rels))/len(src_rels))

    def normaliseCorpus(self,cut_off=0.95,min_quo=0.1):
        # corpus normalisation by a value that is greater or equal to the
        # percentage of weight values given by the cut_off parameter
        # (if the values are below zero, they are set to the min_quo
        # fraction of the minimal normalised value
        ws = sorted(self.corpus.values())
        norm_cons = ws[int(cut_off*len(ws)):][0]
        min_norm = min([x for x in ws if x > 0])*min_quo
        for key in self.corpus:
            w = self.corpus[key]/norm_cons
            if w < 0:
                w = min_norm
            if w > 1:
                w = 1.0
            self.corpus[key] = w

    def computePerspective(self,ptype):
        self.perspectives[ptype] = self.corpus.matricise(PERSP2PIVDIM[ptype])

    def indexSources(self):
        self.sources.index()

    def indexCorpus(self):
        self.corpus.index()

    def indexPerspective(self,ptype):
        self.perspectives[ptype].index()

    def getProvenance(self,statement):
        # getting the statement elements
        s,p,o = statement
        # getting integer ID versions of the statement elements
        if type(s) in [str,str]:
            s = self.lexicon[s]
        if type(p) in [str,str]:
            p = self.lexicon[p]
        if type(o) in [str,str]:
            o = self.lexicon[o]
        # evalating query on the sources tensor and collating the results
        return [x[3] for x, _rel in self.sources.query((s,p,o,None))]

    def getRelevance(self,prov):
        if type(prov) in [str,str]:
            prov = self.lexicon[prov]
        return max(set([rel for _x, rel in \
          self.sources.query((None,None,None,prov))]))

    def exportSources(self,filename,lexicalised=True):
        # export the sources tensor to a file, in a tab-separated value format,
        # either with integer or lexicalised keys
        f = open(filename,'w')
        if lexicalised:
            f.write('\n'.join(['\t'.join([self.lexicon[x] for x in [s,p,o,d]]+\
              [str(w)]) for (s,p,o,d),w in list(self.sources.items())]))
        else:
            f.write('\n'.join(['\t'.join([str(x) for x in [s,p,o,d,w]]) for \
              (s,p,o,d),w in list(self.sources.items())]))
        f.close()

    def exportCorpus(self,filename,lexicalised=True):
        # export the corpus tensor to a file, in a tab-separated value format
        # either with integer or lexicalised keys
        f = open(filename,'w')
        if lexicalised:
            f.write('\n'.join(['\t'.join([self.lexicon[x] for x in [s,p,o]]+[str(w)])\
              for (s,p,o),w in list(self.corpus.items())]))
        else:
            f.write('\n'.join(['\t'.join([str(x) for x in [s,p,o,w]]) for \
              (s,p,o),w in list(self.corpus.items())]))
        f.close()
