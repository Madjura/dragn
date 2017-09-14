"""Object representation of a Paragraph in a text."""
from text.sentence import Sentence


class Paragraph(object):
    """Object representation of a paragraph."""

    def __init__(self, paragraph_id: int, sentences: [Sentence], text=None):
        """
        Constructor.
        :param paragraph_id: The ID of the paragraph in the text. Should be 0-indexed position.
        :param sentences: A list of Sentence objects of sentences contained in this paragraph.
        :param text: Optional. The text this paragraph belongs to.
        """
        self.paragraph_id = paragraph_id
        self.sentences = sentences
        self.text = text
