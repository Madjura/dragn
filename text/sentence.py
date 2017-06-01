class Sentence(object):
    """
    Object representation of POS tagged sentences.
    Has a dictionary of token -> POS-tag pairs.
    """

    def __init__(self, sentence_id: int, tokens: {str: str}):
        """
        Constructor.
            
        Args:
            sentence_id: The id (position in the text) of the sentence.
                The first sentence has the id 0, the second has 1 and so on.
            tokens: A dictionary of token and appropiate POS tag.
        """
        self.sentence_id = sentence_id
        self.tokens = tokens
