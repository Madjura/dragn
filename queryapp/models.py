from django.db import models
from django.db.models import Count


class Text(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TextsAlias(models.Model):
    identifier = models.CharField(max_length=100, unique=True)
    texts = models.ManyToManyField(Text)
    processed = models.BooleanField(default=False)

    @staticmethod
    def for_texts(texts):
        result = TextsAlias.objects.filter(texts__in=texts).annotate(num_texts=Count("texts"))\
            .filter(num_texts=len(texts))
        for r in result:
            if len(r.identifier.split(",")) == len(texts):
                return r
