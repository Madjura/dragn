from django.db import models


# Create your models here.
class InverseIndex(models.Model):
    term = models.CharField(max_length=100)
    index = models.CharField(max_length=100)

    class Meta:
        unique_together = (("term", "index"))
