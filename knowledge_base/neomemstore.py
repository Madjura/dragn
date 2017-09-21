__copyright__ = """
Copyright (C) 2012 Vit Novacek (vit.novacek@deri.org), Digital Enterprise
Research Institute (DERI), National University of Ireland Galway (NUIG)
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

This class is based on the MemStore class of the original system.
The following functions were used from the original system:
    - computeCorpus (renamed to compute_corpus)
    - normaliseCorpus (renamed to normalise_corpus)
    - sorted

    Those functions were used as a base to develop the new ones in this file.
"""
import gzip
import operator
import re
from _collections import defaultdict
from math import log

from knowledge_base.tensor import Tensor
from util import paths

PERSP_TYPES = ['LAxLIRA']


class NeoMemStore(object):
    """
    Used to store / hold relevant "metadata": Which expressions exist, how 
    often they appear in the texts, weighted expressions for further 
    processing.
    """

    def __init__(self):
        # holds token: frequency
        self.lexicon = defaultdict(int)
        # <Expression> close to <Expression2>, ParagraphID: Closeness value
        self.relations = Tensor(rank=4)
        # <Expression> close to <Expression2>: Value
        self.corpus = Tensor(rank=3)
        self.matrix = None

    def incorporate(self, closenesses):
        """
        Incorporates Closeness objects into this NeoMemStore.

        :param closenesses: A list of Closeness objects, as created in  extract_step.
        """
        expressions = []
        # first pass: update lexicon with terms
        for paragraph_closeness in closenesses:
            for closeness in paragraph_closeness:
                expressions += [closeness.term, "close to", closeness.close_to, closeness.paragraph_id]
                key = (closeness.term, "close to", closeness.close_to, closeness.paragraph_id)
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

        :param items: A list of expressions the lexicon is being updated with.
        """
        for item in items:
            self.lexicon[item] += 1

    def compute_corpus(self):
        """
        Computes the corpus based on the relation tuples.
        The corpus is a dictionary mapping the relation tuples to their mutual
        information score, multiplied by their joint frequency.
        """
        # a list of tuples in the format (subject, close to, other, paragraph)
        relation_tuples = self.relations.keys()
        # required for the mutual information score
        relation_count = len(relation_tuples)
        # x -> number of independant occurences
        indep_freq = defaultdict(int)
        # (x, y) -> number of joint occurences
        joint_freq = defaultdict(int)
        # (subject,predicate,objecT) -> (provenance, relevance)
        # subject, predicate, object mapped to provenance, relevance
        relation2provs = defaultdict(lambda: [])
        # going through all the statements in the relations
        for subject, predicate, objecT, provenance in relation_tuples:
            indep_freq[subject] += 1
            indep_freq[objecT] += 1
            joint_freq[(subject, objecT)] += 1
            relation2provs[(subject, predicate, objecT)].append(
                (provenance, self.relations[(subject, predicate, objecT, provenance)])
            )
        # going only through the unique triples now regardless of their provenance
        for subject, predicate, objecT in relation2provs:
            # get the relevances for subject, predicate, object tuples
            # this is the Closeness.closeness value
            relevancy = [x[1] for x in relation2provs[(subject, predicate, objecT)]]
            # get the joint frequency of subject and object
            joint = joint_freq[(subject, objecT)]
            # also get the joint frequency for the other way around
            if (objecT, subject) in joint_freq:
                joint += joint_freq[(objecT, subject)]
            # frequency times mutual information score
            fmi = joint_freq[(subject, objecT)] * log(
                float(relation_count * joint) / (indep_freq[subject] * indep_freq[objecT]), 2)
            # setting the corpus tensor value
            self.corpus[(subject, predicate, objecT)] = fmi * (float(sum(relevancy)) / len(relevancy))

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

        :param cut_off: Optional. Default: 0.95. The limit by which the normalization weight is selected.
        :param min_quo: Optional. Default: 0.1. The normalization factor for the weights that are negative.
        """
        # get all the values from previous step
        weights = sorted(self.corpus.values())
        # take the lowest value of the top percent of weights
        norm_cons = weights[int(cut_off * len(weights)):][0]
        # get the lowest positive value and multiply by min_quo
        try:
            min_norm = min([x for x in weights if x > 0]) * min_quo
        except ValueError:
            min_norm = min_quo
        for key in self.corpus:
            w = self.corpus[key] / norm_cons
            if w < 0:
                w = min_norm
            if w >= 1:
                w = 1.0
            self.corpus[key] = w

    def export(self, path=paths.MEMSTORE_PATH):
        """
        Exports the lexicon, relations and corpus and writes them to 
        disk.
        """
        with (gzip.open(path + "/lexicon.tsv.gz", "w")) as lex_f:
            self.lexicon_to_file(lex_f)
        lex_f.close()

        with (gzip.open(path + "/relations.tsv.gz", "w")) as src_f:
            self.relations.to_file(src_f)
        src_f.close()

        with (gzip.open(path + "/corpus.tsv.gz", "w")) as crp_f:
            self.corpus.to_file(crp_f)
        crp_f.close()

    def import_memstore(self, path=paths.MEMSTORE_PATH):
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

        :param out_file: The file that is being written to.
        """

        for token, frequency in self.lexicon.items():
            line = "\t".join([token, str(frequency)])
            out_file.write(str.encode(line))
            out_file.write(str.encode("\n"))

    def lexicon_from_file(self, lexicon_file):
        """
        Loads the lexicon from a file.

        :param lexicon_file: The file that is being loaded in.
        """
        for line in lexicon_file.read().decode().split("\n"):
            line_split = line.split("\t")
            if len(line_split) != 2:
                continue
            token, frequency = line_split
            self.lexicon[token] = int(frequency)

    def sorted(self, ignored=None, limit=0):
        """
        Sorts the contents of the lexicon.

        :param ignored: A regex of words to be ignored.
        :param limit: How many elements are to be returned.
        :return: Lexicon, but sorted and with only the specified number of items.
        """
        # format is [(expression, frequency), (expression2, frequency2), ...]
        sorted_by_value = [x for x in sorted(self.lexicon.items(),
                                             key=operator.itemgetter(1),
                                             reverse=True)]
        if limit > 0:
            sorted_by_value = sorted_by_value[:limit]  # from 0 to limit
        elif limit <= 0 and ignored:
            sorted_by_value_with_limit = []
            for frequency in sorted_by_value:
                if not re.search(ignored, frequency[0]):
                    sorted_by_value_with_limit.append(frequency)
            avg = sum(x[1] for x in sorted_by_value_with_limit) / float(len(sorted_by_value_with_limit))
            sorted_by_value = [x[0] for x in sorted_by_value_with_limit if x[1] >= avg]
        return sorted_by_value
