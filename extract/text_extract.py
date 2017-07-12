"""
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

The following functions were used from the original system:
    - get_cooc
    - text2cooc
    - gen_src (renamed to generate_source)

    Those functions were used as a base to develop the new ones in this file.
"""

import math
from _collections import OrderedDict, defaultdict
from itertools import combinations

import nltk
from nltk.chunk.regexp import RegexpParser
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

from text.closeness import Closeness
from text.sentence import Sentence

NP_GRAMMAR_COMPOUND = """
NP: {<JJ.*>*(<N.*>|<JJ.*>)+((<IN>|<TO>)?<JJ.*>*(<N.*>|<JJ.*>)+)*((<CC>|,)<JJ.*>*(<N.*>|<JJ.*>)+((<IN>|<TO>)?<JJ.*>*(<N.*>|<JJ.*>)+)*)*}
"""
NP_GRAMMAR_SIMPLE = """
NP: {<JJ.*>*(<N.*>|<JJ.*>)+}
"""


def split_paragraphs(text: str) -> [str]:
    """
    Takes a text and collects the paragraphs of the text.
    
        Args:
            text: The input string. Unmodified, keep it as is. Supposed to be
                the content of a file read with .read().
        Returns:
            A list of strings, where each element is a paragraph of the original
            text.
    """
    lines = text.split("\n")
    current_paragraph = []
    paragraphs = []

    # iterate over each line of the text, with .strip() applied to remove
    # trailing whitespace
    for line in map(lambda x: x.strip(), lines):
        if len(line) > 0:
            # the line is NOT a paragraph if there is something there
            current_paragraph.append(line)
        elif current_paragraph:
            # line IS a paragraph
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph.clear()
    # get the final paragraph
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    return paragraphs


def pos_tag(text: str) -> [Sentence]:
    """
    Tokenize a given text and generates a list of Sentence objects.
        
        Args:
            text: The input text that is to be POS tagged.
        Returns:
            A list of Sentence objects.
    """
    sentences = []
    for count, sentence in enumerate(nltk.sent_tokenize(text)):
        tokens = OrderedDict()
        # get the tokens and POS tags
        for word, tag in nltk.pos_tag(nltk.word_tokenize(sentence)):
            tokens[word] = tag
            # sentence is now tokenized and tokens have POS tags
        sentences.append(Sentence(count, tokens))
    return sentences


def parse_pos(sentences: [Sentence]) -> {int, (str, str)}:
    """
    Parses a POS-tagged file and return a dictionary of sentence number -> list 
    of (token,POS-tag) tuples.
    
        Args:
            sentences: A list of Sentence objects.
        Returns:
            A dictionary where the keys are the id of a sentence and the values
            are a list of tuples, with the tuples in the 
            format of (token, POS-tag).
    """
    dictionary = {}
    for sentence in sentences:
        dictionary[sentence.sentence_id] = [(token, tag)
                                            for token, tag in sentence.tokens.items()]
    return dictionary


def text2cooc(pos_dictionary: {int, (str, str)},
              add_verbs=True,
              language="english") -> {str, list}:
    """
    Processes the input dictionary in the format:
        {sentence_id: [(Token, POS-tag),}
    and returns a dictionary mapping tokens to ID of the sentence they appear 
    in.
    """
    parser_cmp = RegexpParser(NP_GRAMMAR_COMPOUND)
    term2sentence_id = {}
    lemmatizer = WordNetLemmatizer()

    for sentence_id, pos_tagged_tokens in pos_dictionary.items():
        if add_verbs:
            # updating the inverse occurrence index with verbs
            for subject, tag in pos_tagged_tokens:
                # check if subject is tagged as a verb
                # Penn Treebank uses VB for all verbs
                # for more details see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
                if tag.startswith("VB"):
                    verb = lemmatizer.lemmatize(subject, "v").lower()
                    if verb not in stopwords.words(language):
                        if verb not in term2sentence_id:
                            term2sentence_id[verb] = set()
                        term2sentence_id[verb].add(sentence_id)
        # trying to parse the sentence_id into a top-level chunk tree
        tree = parser_cmp.parse(pos_dictionary[sentence_id])
        # getting the top-level tree triples and decomposing the NPs
        cmp_triples, simple_trees = get_cooc([tree], stoplist=False,
                                             language=language)
        smp_triples, _ = get_cooc(simple_trees, stoplist=True,
                                  language=language)
        # updating the inverse occurrence index with NPs 
        for subject, _, objecT in cmp_triples + smp_triples:
            if subject.lower() not in term2sentence_id:
                term2sentence_id[subject.lower()] = set()
            if objecT.lower() not in term2sentence_id:
                term2sentence_id[objecT.lower()] = set()
            term2sentence_id[subject.lower()].add(sentence_id)
            term2sentence_id[objecT.lower()].add(sentence_id)
    return term2sentence_id


def get_cooc(chunk_trees, stoplist=True, language="english"):
    """
    Parses a chunk tree and gets co-occurance of terms.
    
        Args:
            chunk_trees: Tree from the NLTK RegexParser.
            stoplist: Optional. Default: True.
                Whether or not stopwords are to be removed.
            language: Optional. Default: "english".
                The language of the texts.
    """
    triples = []
    simple_trees = []
    lemmatizer = WordNetLemmatizer()  # from nltk
    parser_simple = RegexpParser(NP_GRAMMAR_SIMPLE)  # from nltk
    for t in chunk_trees:
        entities = []
        for chunk in t:
            if isinstance(chunk, Tree) and chunk.label() == 'NP':
                # getting a tree for later processing of triples from the simple noun 
                # phrases (if present)
                simple_trees.append(parser_simple.parse(chunk.leaves()))
                words = []
                for word, tag in chunk:
                    if (stoplist and word in stopwords.words(language)) or \
                            (not any(char.isalnum() for char in word)):
                        # do not process stopwords for simple trees, do not process purely 
                        # non alphanumeric characters
                        continue
                    if tag.startswith('N'):
                        words.append(lemmatizer.lemmatize(word, 'n'))
                    elif tag.startswith('J'):
                        words.append(lemmatizer.lemmatize(word, 'a'))
                    else:
                        words.append(word)
                if len(words) > 0:
                    entities.append("_".join(words))
                    # experimental
                    #entities.extend(words)
        for e1, e2 in combinations(entities, 2):
            triples.append((e1, "close to", e2))
            triples.append((e2, "close to", e1))
    return triples, simple_trees


def generate_source(token2sentences: dict,
                    *,
                    paragraph_id: object = str,
                    distance_threshold: int = 5,
                    weight_threshold: float = 1 / 3) -> object:
    """
    Generates source/statement (srcstm) for following steps.
    
        Args:
            token2sentences: A dictionary in the format 
                    {str: List[int]},
                from text2cooc function.
            paragraph_id: The ID of the paragraph the text2sentences dictionary
                belongs to.
            distance_threshold: Optional. Default: 5.
                How far apart terms may be to be still considered close 
                / relevant to each other.
            weight_threshold: Optional. Default: 1/3.
                The minimum weight.
        Returns:
            A list of Closeness objects, representing the "relatedness" of
            the terms in the sentences of token2sentences.
    """

    closeness_list = []

    # get all term combinations to see if they are close to each other
    for term1, term2 in combinations(list(token2sentences.keys()), 2):
        w = 0.0

        # get positions of first term
        # positions are always per paragraph
        for position1 in token2sentences[term1]:

            # get positions of second term
            for position2 in token2sentences[term2]:

                # get the distance between the terms, measured in "terms between"
                distance = math.fabs(position1 - position2)

                # check if terms are close enough to each other
                if distance < distance_threshold:
                    # calculate new weight
                    w += 1 / (1 + distance)

        # check if terms are relevant enough
        if w > weight_threshold:
            closeness_list.append(Closeness(term1, term2, w, paragraph_id))

    w2statements = defaultdict(list)
    for closeness in closeness_list:
        w2statements[closeness.closeness].append(closeness)
    # get weight values in descending orders - why?
    keys = list(w2statements.keys())
    keys.sort(reverse=True)
    new_lines = []

    # get list of closeness, ordered by descending weight
    for key in keys:
        for closeness in w2statements[key]:
            new_lines.append(closeness)
    return new_lines

if __name__ == "__main__":
    p = RegexpParser(NP_GRAMMAR_COMPOUND)
    sentence = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"),
                ("dog", "NN"), ("outside", "IN"), ("Innsmouth", "NNP")]
    print(p.parse(sentence))