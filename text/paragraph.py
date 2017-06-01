from text.sentence import Sentence


class Paragraph(object):
    """Object representation of a pargraph."""

    def __init__(self, paragraph_id: int, sentences: [Sentence], text=None):
        """
        Constructor.
        
        Args:
            paragraph_id: The id (position) of the paragraph in the text.
            sentences: A list of sentences in the paragraph.
        """

        self.paragraph_id = paragraph_id
        self.sentences = sentences
        self.text = text
