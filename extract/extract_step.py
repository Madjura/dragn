import django
django.setup()

from os.path import os                                         
import pickle

from extract.text_extract import split_paragraphs, pos_tag, parse_pos, text2cooc,\
    generate_source
from text.paragraph import Paragraph
from util import paths
#==============================================================================
# from django.db.utils import IntegrityError
# from text_app.models import TextModel, ParagraphModel, SentenceModel,\
#     TokenModel
#==============================================================================

#==============================================================================
# 
# def extract_step_django():
#     for f in os.listdir(paths.TEXT_PATH):
#         text = f
#         if not text.endswith(".txt"):
#             continue
#         with (open(paths.TEXT_PATH+"/" + f, "r")) as current_text:
#             new_text = TextModel(title=text)
#             try:
#                 # TODO: CHECK IF TEXT EXISTS
#                 # save the new text
#                 new_text.save()
#                 text_content = current_text.read()
#                 paragraphs = split_paragraphs(text_content)
#                 for count, paragraph in enumerate(paragraphs):
#                     
#                     # create paragraph model objects
#                     new_paragraph = ParagraphModel(text=new_text)
#                     new_paragraph.save()
#                     sentences = pos_tag(paragraph) # sentence objects
#                     for sentence in sentences:
#                         new_sentence = SentenceModel(paragraph=new_paragraph, position=count)
#                         
#                         # set up sentences
#                         new_sentence.save()
#                         tokens = sentence.tokens
#                         for token, pos in tokens.items():
#                             
#                             # set up tokens in each sentence
#                             new_token = TokenModel(token=token, pos_tag=pos, sentence=new_sentence)
#                             new_token.save()
#                             
#                         # parse the pos-tagged sentences into the dictionary format
#                         pos_tagged_parsed = parse_pos(new_paragraph.get_sentence_list())
#                         
#                         text2sentence = text2cooc(pos_tagged_parsed)
#                         
#                         closeness = generate_source(text2sentence, count)
#                         print(closeness)
#             except IntegrityError:
#                 pass # the text was already processed
#                 
#==============================================================================
#extract_step_django()
#exit()


# equivalent to exst step
# STEP 1
for file in os.listdir(paths.TEXT_PATH):
    text = file
    if not file.endswith(".txt"):
        continue
    with (open(paths.TEXT_PATH + "/" + file, "r")) as current_text:
        
        text_content = current_text.read()
        # Split the text into paragraphs first
        paragraphs = split_paragraphs(text_content)
        pickle.dump(paragraphs, open(paths.PARAGRAPHS_PATH + "/" + file + ".par", "wb"))
        
        # take each paragraph, pos tag each paragraph content
        # represents text2postag call
        paragraph_list = []
        closeness = []
        for count, paragraph in enumerate(paragraphs):
            
            # make new paragraph, with pos-tagged sentence list
            new_paragraph = Paragraph(count, pos_tag(paragraph), text)
            paragraph_list.append(new_paragraph)
            
            # parse the pos-tagged sentences into the dictionary format
            pos_tagged_parsed = parse_pos(new_paragraph.sentences)
            # example: {0: [('A', 'DT'), ('Study', 'NNP'), ('in', 'IN'), ('Temperament', 'NNP')]}
            
            text2sentence = text2cooc(pos_tagged_parsed)
            
            closeness_list = generate_source(text2sentence, text + "_"+str(count))
            closeness.append(closeness_list)
            pickle.dump(text2sentence, open(paths.TOKEN_TO_SENTENCE_PATH + "/" \
                        + str(new_paragraph.paragraph_id) + ".t2s", "wb"))
        
        """
        format is:
        [ closenesses of paragraph
            [closeness of sentence in the paragraph]
        ]
        """
        pickle.dump(paragraph_list, open(paths.POS_PATH + "/" + text + ".p", "wb")) # used to be .pos
        pickle.dump(closeness, open(paths.CLOSENESS_PATH + "/" + "closeness.p", "wb")) # used to be .tsv
        
        ### NEXT STEP: knowledge_base_create_step