from os.path import os                                         
import pickle

from extract.text_extract import split_paragraphs, pos_tag, parse_pos, text2cooc,\
    generate_source
from text.paragraph import Paragraph
from util import paths

# equivalent to exst step
# STEP 1
for file in os.listdir(paths.TEXT_PATH):
    text = file
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
            
            ## feed the .t2s into gen_src
            ## TODO: do something with what this returns, see next step
            closeness.append(generate_source(text2sentence, count))
            
            pickle.dump(text2sentence, open(paths.TOKEN_TO_SENTENCE_PATH + "/" \
                        + str(new_paragraph.paragraph_id) + ".t2s", "wb"))
        
        """
        format is:
        [ closenesses of paragraph
            [closeness of sentence in the paragraph]
        ]
        """
        pickle.dump(paragraph_list, open(paths.POS_PATH + "/" + file + ".pos", "wb"))
        pickle.dump(closeness, open(paths.CLOSENESS_PATH + "/closeness.tsv", "wb"))