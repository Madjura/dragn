"""Object representation of the weighted distance between two tokens in a text."""


class Closeness(object):
    """
    Object representation to describe how close/relevant two terms are to each
    other.
    """

    def __init__(self, term, close_to, closeness, paragraph_id=-1):
        """
        Constructor.
        :param term: A token from a text.
        :param close_to: A token the first token is close to.
        :param closeness: The weighted distance between the two.
        :param paragraph_id: Optional. The ID of the paragraph they appear in.
        """
        self.term = term
        self.close_to = close_to
        self.paragraph_id = paragraph_id
        self.closeness = closeness

    def __str__(self):
        """
        :return: String representation of this Closeness object for better understandability.
        """
        return "Term: " + self.term + "\nClose to:" + self.close_to + "\nParagraph id:" + str(
            self.paragraph_id) + "\nCloseness:" + str(self.closeness)
