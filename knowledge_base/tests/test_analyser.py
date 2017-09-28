"""Tests for the analyser module / knowledge_base package."""
import unittest

import math

from extract.text_extract import split_paragraphs, pos_tag, extract_from_sentences
from knowledge_base.analyser import Analyser
from knowledge_base.tensor import Tensor


class TextAnalyser(unittest.TestCase):

    def test_similarity_calculation(self):
        tensor = Tensor(rank=3)
        tensor[("apple", "close to", "tree")] = 0.9
        tensor[("apple", "close to", "leaf")] = 0.5
        tensor[("tree", "close to", "apple")] = 0.9
        tensor[("tree", "close to", "leaf")] = 0.6
        tensor[("leaf", "close to", "apple")] = 0.5
        tensor[("leaf", "close to", "tree")] = 0.6
        tensor[("leaf", "close to", "fruit")] = 0.4
        tensor[("fruit", "close to", "leaf")] = 0.4
        matrix = tensor.matricise(0)
        analyser = Analyser(matrix=matrix, trace=True)
        similar = analyser.similar_to("tree", top=10)
        for (similar_token, similarity) in similar:
            if similar_token == "apple":
                assert math.isclose(similarity, 0.3/(1.08*1.03), abs_tol=0.001)
            if similar_token == "leaf":
                assert(math.isclose(similarity, 0.45/(1.081*0.877), abs_tol=0.001))


if __name__ == "__main__":
    unittest.main()
