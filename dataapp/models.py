"""Models for dataapp."""
from django.db import models


class InverseIndex(models.Model):
    """
    Model for the inverted index.
    Each entry represents a (term, document) pair.
    """
    term = models.CharField(max_length=100)
    index = models.CharField(max_length=100)

    class Meta:
        unique_together = ("term", "index")
