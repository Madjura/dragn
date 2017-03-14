from _collections import defaultdict
from knowledge_base.tensor import Tensor
from math import log
import os
import gzip
import operator

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

class NeoMemStore(object):
    
    def __init__(self):
        """
        Format will be:
            <expression>: <frequency>
        """
        self.lexicon = defaultdict(int)
        self.sources = Tensor(rank=4)
        self.corpus = Tensor(rank=3)
        self.perspectives = dict([(x,Tensor(rank=2)) for x in PERSP_TYPES])

    def incorporate(self, closenesses):
        expressions = []
        
        # first pass: update lexicon with terms
        for paragraph_closeness in closenesses:
            for closeness in paragraph_closeness:
                expressions += [closeness.term, "close to", closeness.close_to, closeness.paragraph_id]
        self.update_lexicon(expressions)
        
        for paragraph_closeness in closenesses:
            for closeness in paragraph_closeness:
                key = (closeness.term, "close to", closeness.close_to, closeness.paragraph_id)
                self.sources[key] = closeness.closeness
                
    def update_lexicon(self, items):
        if type(items) is str:
            items = list(items)
        for item in items:
            self.lexicon[item] += 1
            
    def computeCorpus(self):
        ### mostly untouched
        
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
        ### untouched
        
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
            
    def export(self, path, compress=True):
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
        self.lexicon_to_file(lex_f)
        self.sources.to_file(src_f)
        self.corpus.to_file(crp_f)
        lex_f.close()
        src_f.close()
        crp_f.close()
        
    def import_memstore(self, path, compress=True):
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
        self.lexicon_from_file(lex_f)
        self.sources.from_file(src_f)
        self.corpus.from_file(crp_f)
        lex_f.close()
        src_f.close()
        crp_f.close()

        
    def lexicon_to_file(self, filename):
        # exporting a lexicon - inverse to import
        for phrase, frequency in self.lexicon.items():
            line = '\t'.join( [ phrase, str(frequency)] ) + '\n'
            try:
                filename.write(str.encode(line))
            except AttributeError:
                # assuming a filename
                with open(filename, "w") as f:
                    f = open(filename,'w')
                    f.write(line)
                    f.close()
                    return
        filename.flush()
        os.fsync(filename.fileno())
        
    def lexicon_from_file(self, filename):
        # import a lexicon from a tab-separated file (including the index mapping
        # and frequency of the token); expected format: token index frequency
        # assuming a file object
        weird_lines = []
        tmp = str(filename.read())
        tmp = tmp.replace("\\t", "\t")
        tmp = tmp.split("\\n")
        lines = tmp
        for line in lines:
            separated = line.split("\t")
            if len(separated) != 2:
                weird_lines.append(line)
                continue
            expression = separated[0]
            frequency = int(separated[1])
            self.lexicon[expression] = frequency
        print("NUMBER OF WEIRD LINES: ", len(weird_lines), weird_lines)
        
    def sorted(self):
        ### TODO: return only if value > average, see his code
        sorted_by_value = [x[0] for x in sorted(self.lexicon.items(), key=operator.itemgetter(1), reverse=True)]
        return sorted_by_value
    
    def computePerspective(self,ptype):
        self.perspectives[ptype] = self.corpus.matricise(PERSP2PIVDIM[ptype])