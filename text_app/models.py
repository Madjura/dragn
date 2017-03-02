from django.db import models
from text.sentence import Sentence

class TextModelManager(models.Manager):
    def for_title(self, title):
        return self.get_queryset().filter(title=title)[0]
    
# Create your models here.
class TextModel(models.Model):
    title = models.CharField(max_length=100, default="DEFAULT_TITLE", unique=True)
    objects = TextModelManager()
    
class ParagraphModel(models.Model):
    text = models.ForeignKey(TextModel)
    
    def get_sentence_list(self):
        sentences = SentenceModel.objects.filter(paragraph=self)
        sentence_list = []
        for sentence in sentences:
            tokens = TokenModel.to_dictionary(TokenModel.objects.filter(sentence=sentence))
            sentence_list.append(Sentence(sentence.position, tokens))
        return sentence_list
        
class SentenceModel(models.Model):
    paragraph = models.ForeignKey(ParagraphModel)
    position = models.IntegerField()
        
class TokenModel(models.Model):
    token = models.CharField(max_length=100, default="DEFAULT_TOKEN")
    pos_tag = models.CharField(max_length=5, default="DEFAULT_TAG")
    sentence = models.ForeignKey(SentenceModel)
    
    @staticmethod
    def to_dictionary(tokens):
        token_dictionary = {}
        for token in tokens:
            token_dictionary[token.token] = token.pos_tag
        return token_dictionary
        
class ClosenessModel(models.Model):
    term = models.CharField(max_length=100, default="DEFAULT_TERM")
    close_to = models.CharField(max_length=100, default="DEFAULT_CLOSETO")
    closeness = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    
    def __str__(self):
        return self.term + " close to " + self.close_to + " with closeness: " + str(self.closeness)