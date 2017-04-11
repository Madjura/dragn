from _collections import defaultdict
from knowledge_base.tensor import Tensor
from math import log
import os
import gzip
import operator
from util import paths
from numpy.core.fromnumeric import sort
import re
from http.cookiejar import vals_sorted_by_key

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
    """
    Used to store / hold relevant "metadata": Which expressions exist, how often
    they appear in the texts, weighted expressions for further processing.
    """
    
    
    def __init__(self):
        # Format: <expression>: <frequency>
        self.lexicon = defaultdict(int)
        
        # <Expression> close to <Expression2>, ParagraphID: Closeness value
        self.sources = Tensor(rank=4)
        
        # <Expression> close to <Expression2>: Value
        self.corpus = Tensor(rank=3)
        self.perspectives = dict([(x, Tensor(rank=2)) for x in PERSP_TYPES])

    def incorporate(self, closenesses: ["Closeness"]) -> None:
        """
        Incorporates Closeness objects into this NeoMemStore.
            
            Args:
                closenesses: A list of Closeness objects, as created in extract_step.
        """
        
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
        """
        Helper function to fill the lexicon with how often each expression 
        appears in "close to" relations.
        Example:
            [understand] = 42
            "understand" appears in 42 "X close to Y" relations.
        Used to find the "most relevant" expressions to boost the speed by taking
        only the most common ones into account.
        
            Args:
                items: A list of expressions the lexicon is being updated with.
        """
        
        if type(items) is str:
            items = list(items)
        for item in items:
            self.lexicon[item] += 1
            
    def compute_corpus(self):
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
        spo2pr = defaultdict(lambda: [])
        
        # going through all the statements in the sources
        for s, p, o, paragraph_id in list(self.sources.keys()):
            N += 1
            ### refactored to use defaultdict
            indep_freq[s] += 1
            indep_freq[o] += 1
            joint_freq[(s, o)] += 1
            tripl_freq[(s, p, o)] += 1
            spo2pr[(s, p, o)].append((paragraph_id, self.sources[(s, p, o, paragraph_id)]))
        # going only through the unique triples now regardless of their provenance
        for s, p, o in spo2pr:
            # a list of relevances of particular statement sources
            src_rels = [x[1] for x in spo2pr[(s,p,o)]]
            ### src rels has sometimes more than 1 value
            
            # absolute frequency of the triple times it's mutual information score
            joint = joint_freq[(s, o)]
            if (o, s) in joint_freq:
                ### o and s are terms
                joint += joint_freq[(o, s)]
            # frequency times mutual information score
            fMI = 0.0
            try:
                fMI = tripl_freq[(s, p, o)] * log(float(N * joint) / (indep_freq[s] * indep_freq[o]), 2)
            except ValueError:
                continue
            # setting the corpus tensor value
            self.corpus[(s, p, o)] = fMI * (float(sum(src_rels))/len(src_rels))
            
    def normalise_corpus(self, cut_off=0.95, min_quo=0.1):
        ### untouched
        
        # corpus normalisation by a value that is greater or equal to the
        # percentage of weight values given by the cut_off parameter
        # (if the values are below zero, they are set to the min_quo
        # fraction of the minimal normalised value
        ws = sorted(self.corpus.values())
        norm_cons = ws[int(cut_off * len(ws)):][0]
        min_norm = min([x for x in ws if x > 0]) * min_quo
        for key in self.corpus:
            w = self.corpus[key]/norm_cons
            if w < 0:
                w = min_norm
            if w > 1:
                w = 1.0
            self.corpus[key] = w
            
    def export(self, path=paths.MEMSTORE_PATH_EXPERIMENTAL):
        """Exports the lexicon, sources and corpus and writes them to disk."""
        
        with (gzip.open(path + "/lexicon.tsv.gz" , "w")) as lex_f:
                self.lexicon_to_file(lex_f)
        lex_f.close()
        
        with (gzip.open(path + "/sources.tsv.gz", "w")) as src_f:
            self.sources.to_file(src_f)
        src_f.close()
        
        with (gzip.open(path + "/corpus.tsv.gz", "w")) as crp_f:
            self.corpus.to_file(crp_f)
        crp_f.close()
        
    def import_memstore(self, path=paths.MEMSTORE_PATH_EXPERIMENTAL):
        """Imports the lexicon, sources and corpus from disk."""
        
        with (gzip.open(path + "/lexicon.tsv.gz", "rb")) as lexicon_file:
            self.lexicon_from_file(lexicon_file)
        lexicon_file.close()
        
        with (gzip.open(path + "/sources.tsv.gz", "rb")) as sources_file:
            self.sources.from_file(sources_file)
        sources_file.close()
        
        with (gzip.open(path + "/corpus.tsv.gz", "rb")) as corpus_file:
            self.corpus.from_file(corpus_file)
        corpus_file.close()
        
    def lexicon_to_file(self, out_file):
        # exporting a lexicon - inverse to import
        for phrase, frequency in self.lexicon.items():
            line = '\t'.join( [ phrase, str(frequency)] ) + '\n'
            out_file.write(str.encode(line))
        out_file.flush()
        os.fsync(out_file.fileno())
        
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
        
    def sorted(self, ignored=None, limit=0):
        ### TODO: return only if value > average, see his code
        print(self.lexicon.items())
        
        # format is [(expression, frequency), (expression2, frequency2), ...]
        sorted_by_value = [x for x in sorted(self.lexicon.items(), key=operator.itemgetter(1), reverse=True)]
        
        print("NeoMemStore, sorted. ~ LENGTH OF SORTED BY VALUE WITHOUT LIMIT IS ", len(sorted_by_value))
        if limit > 0:
            sorted_by_value = sorted_by_value[:limit] # from 0 to limit
        elif limit <= 0 and ignored:
            # < included to handle that case as well
            
            sorted_by_value_with_limit = []
            for frequency in sorted_by_value:
                if not re.search(ignored, frequency[0]):
                    sorted_by_value_with_limit.append(frequency)
            avg = sum(x[1] for x in sorted_by_value_with_limit) / float(len(sorted_by_value_with_limit))
            print("NeoMemStore, sorted. ~ THE AVERAGE IS: ", avg)
            sorted_by_value = [x[0] for x in sorted_by_value_with_limit if x[1] >= avg]
            print("NeoMemStore, sorted. ~ NEW LENGTH WITH LIMIT: ", len(sorted_by_value))
        return sorted_by_value

    def computePerspective(self,ptype):
        self.perspectives[ptype] = self.corpus.matricise(PERSP2PIVDIM[ptype])