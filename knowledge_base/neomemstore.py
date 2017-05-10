from _collections import defaultdict
from knowledge_base.tensor import Tensor
from math import log
import os
import gzip
import operator
from util import paths
import re

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
        # holds token: frequency
        self.lexicon = defaultdict(int)
        
        # <Expression> close to <Expression2>, ParagraphID: Closeness value
        self.relations = Tensor(rank=4)
        
        # <Expression> close to <Expression2>: Value
        self.corpus = Tensor(rank=3)
        
        self.perspectives = dict([(x, Tensor(rank=2)) for x in PERSP_TYPES])

    def incorporate(self, closenesses: ["Closeness"]):
        """
        Incorporates Closeness objects into this NeoMemStore.
            
            Args:
                closenesses: A list of Closeness objects, as created in extract_step.
        """
        
        expressions = []
        
        # first pass: update lexicon with terms
        for paragraph_closeness in closenesses:
            for closeness in paragraph_closeness:
                expressions += [closeness.term, "close to", closeness.close_to, 
                                closeness.paragraph_id]
                key = (closeness.term, "close to", closeness.close_to, 
                       closeness.paragraph_id)
                self.relations[key] = closeness.closeness
        self.update_lexicon(expressions)
                
    def update_lexicon(self, items: [str]):
        """
        Helper function to fill the lexicon with how often each expression 
        appears in "close to" relations.
        Example:
            [understand] = 42
            "understand" appears in 42 "X close to Y" relations.
        Used to find the "most relevant" (those that appear in most statements)
        expressions to boost the speed by ignoring the others.
        
            Args:
                items: A list of expressions the lexicon is being updated with.
        """
        
        for item in items:
            self.lexicon[item] += 1
            
    def compute_corpus(self):
        """
        Computes the corpus based on the relation tuples.
        The corpus is a dictionary mapping the relation tuples to their mutual
        information score, multiplied by their joint frequency.
        """
        
        # a list of tuples in the format (token, close to, other, paragraph)
        relation_tuples = self.relations.keys()
        
        # required for the mutual information score
        relation_count = len(relation_tuples)
        
        # x -> number of independant occurences
        indep_freq = defaultdict(int)
        
        # (x, y) -> number of joint occurences
        joint_freq = defaultdict(int)
        
        # (token,related_to,token2) -> (provenance, relevance)
        # token, related_to, object mapped to provenance, relevance
        relation2provs = defaultdict(lambda: [])
        
        # going through all the statements in the relations
        for token, related_to, token2, provenance in relation_tuples:
            indep_freq[token] += 1
            indep_freq[token2] += 1
            joint_freq[(token, token2)] += 1
            relation2provs[(token, related_to, token2)].append(
                (provenance, 
                 self.relations[(token, related_to, token2, provenance)]
                 ))
        # going only through the unique triples now regardless of their provenance
        for token, related_to, token2 in relation2provs:
            # get the relevances for token, related_to, object tuples
            # this is the Closeness.closeness value
            relevancy = [x[1] for x in relation2provs[(token,related_to,token2)]]
            # get the joint frequency of token and object
            joint = joint_freq[(token, token2)]
            
            # also get the joint frequency for the other way around
            if (token2, token) in joint_freq:
                joint += joint_freq[(token2, token)]
                
            # frequency times mutual information score
            fMI = joint_freq[(token, token2)] * log(float(relation_count * joint) / (indep_freq[token] * indep_freq[token2]), 2)

            # setting the corpus tensor value
            self.corpus[(token, related_to, token2)] = fMI * (float(sum(relevancy))/len(relevancy))
            
    def normalise_corpus(self, cut_off=0.95, min_quo=0.1):
        """
        Normalizes the corpus as follows:
            1) Get the calculated corpus weights from compute_corpus()
            2) Get the top (1-X)*100% of weights.
                X is based on cut_off, default is 0.95.
                For that value, the top 5% weights are considered.
            3) Get the lowest weight value from step 2).
                Example:
                    Assume the weights are a list from 1 to 100.
                    Step 2 would get a list from 96 to 100:
                    [96, 97, 98, 99, 100], the 5% top values.
                    The lowest value would be 96.
            4) Get the lowest, non-negative weight and multiply it by min_quo.
            5) Then, for each corpus weight:
                5.1) Divide by the value from 3).
                5.2) If the new weight is negative, set it instead to the 
                    value from 4).
                5.3) If the new weight is greater or equal 1, set it to 1.0.
                5.4) Replace the old weight with the new one from step 5.
                
            Args:
                cut_off: Optional. Default: 0.95. The limit by which the 
                    normalization weight is selected.
                min_quo: Optional. Default: 0.1. The normalization factor for
                    the weights that are negative.
        """
        
        # get all the values from previous step
        weights = sorted(self.corpus.values())
        
        # take the lowest value of the top percent of weights
        norm_cons = weights[int(cut_off * len(weights)):][0]
        
        # get the lowest positive value and multiply by min_quo
        min_norm = min([x for x in weights if x > 0]) * min_quo
        for key in self.corpus:
            w = self.corpus[key]/norm_cons
            if w < 0:
                w = min_norm
            if w >= 1:
                w = 1.0
            self.corpus[key] = w
            
    def export(self, path=paths.MEMSTORE_PATH_EXPERIMENTAL):
        """Exports the lexicon, relations and corpus and writes them to disk."""
        
        with (gzip.open(path + "/lexicon.tsv.gz" , "w")) as lex_f:
                self.lexicon_to_file(lex_f)
        lex_f.close()
        
        with (gzip.open(path + "/relations.tsv.gz", "w")) as src_f:
            self.relations.to_file(src_f)
        src_f.close()
        
        with (gzip.open(path + "/corpus.tsv.gz", "w")) as crp_f:
            self.corpus.to_file(crp_f)
        crp_f.close()
        
    def import_memstore(self, path=paths.MEMSTORE_PATH_EXPERIMENTAL):
        """Imports the lexicon, relations and corpus from disk."""
        
        with (gzip.open(path + "/lexicon.tsv.gz", "r")) as lexicon_file:
            self.lexicon_from_file(lexicon_file)
        lexicon_file.close()
        
        with (gzip.open(path + "/relations.tsv.gz", "rb")) as sources_file:
            self.relations.from_file(sources_file)
        sources_file.close()
        
        with (gzip.open(path + "/corpus.tsv.gz", "rb")) as corpus_file:
            self.corpus.from_file(corpus_file)
        corpus_file.close()
        
    def lexicon_to_file(self, out_file):
        """
        Writes the lexicon dictionary to a file in the format:
            token\tfrequency\n
            
            Args:
                out_file: The file that is being written to.
        """
        
        for token, frequency in self.lexicon.items():
            line = "\t".join([token, str(frequency)])
            out_file.write(str.encode(line))
            out_file.write(str.encode("\n"))
        
    def lexicon_from_file(self, lexicon_file):
        """
        Loads the lexicon from a file.
        
            Args:
                lexicon_file: The file that is being loaded in.
        """
        
        weird_lines = []
        for line in lexicon_file.read().decode().split("\n"):
            line_split = line.split("\t")
            if len(line_split) != 2:
                weird_lines.append(line)
                continue
            expression, frequency = line_split
            self.lexicon[expression] = int(frequency)
        print("NUMBER OF WEIRD LINES: ", len(weird_lines), weird_lines)
        
    def sorted(self, ignored=None, limit=0):
        # format is [(expression, frequency), (expression2, frequency2), ...]
        sorted_by_value = [x for x in sorted(self.lexicon.items(), key=operator.itemgetter(1), reverse=True)]
        
        if limit > 0:
            sorted_by_value = sorted_by_value[:limit] # from 0 to limit
        elif limit <= 0 and ignored:            
            sorted_by_value_with_limit = []
            for frequency in sorted_by_value:
                if not re.search(ignored, frequency[0]):
                    sorted_by_value_with_limit.append(frequency)
            avg = sum(x[1] for x in sorted_by_value_with_limit) / float(len(sorted_by_value_with_limit))
            sorted_by_value = [x[0] for x in sorted_by_value_with_limit if x[1] >= avg]
        return sorted_by_value

    def computePerspective(self, ptype):
        self.perspectives[ptype] = self.corpus.matricise(PERSP2PIVDIM[ptype])