class Closeness(object):
    """
    Object representation to describe how close/relevant two terms are to each
    other.
    """


    def __init__(self, term, close_to, closeness, paragraph_id = -1):
        """
        Constructor
            
            Args:
                term: A term.
                close_to: Another term that the first one is relevant/close to.
                closeness: Distance / Relevance the terms have to each other.
                paragraph_id: Optional. Defaults to -1 when not set.
                    The ID of the paragraph the terms appear in.
        """
        
        self.term = term
        self.close_to = close_to
        self.paragraph_id = paragraph_id
        self.closeness = closeness
        
    def __str__(self):
        return "Term: " + self.term + "\nClose to:" + self.close_to + "\nParagraph id:" + str(self.paragraph_id) + "\nCloseness:" + str(self.closeness)