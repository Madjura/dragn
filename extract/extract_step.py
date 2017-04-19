from os.path import os                                         
import pickle
from extract.text_extract import split_paragraphs, pos_tag, parse_pos, text2cooc,\
    generate_source
from text.paragraph import Paragraph
from util import paths

def make_folders():
    for path in paths.ALL:
        if not os.path.exists(path):
            os.makedirs(path)

def extract_step(text_path: str=paths.TEXT_PATH):
    # STEP 1
    
    # iterate over texts
    closeness = []
    for text in os.listdir(paths.TEXT_PATH):
        if not text.endswith(".txt"):
            continue
        with (open(paths.TEXT_PATH + "/" + text, "r", encoding="utf8")) as current_text:
            text_content = current_text.read()
            
            # split the text into paragraphs first
            paragraphs = split_paragraphs(text_content)
            
            # TODO: is this even being used still?
            pickle.dump(paragraphs, open(paths.PARAGRAPHS_PATH + "/" + text + ".par", "wb"))
            
            # take each paragraph, pos tag each paragraph content
            paragraph_list = []
            for count, paragraph in enumerate(paragraphs):
                
                # make new paragraph, with pos-tagged sentence list
                new_paragraph = Paragraph(count, pos_tag(paragraph), text)
                paragraph_list.append(new_paragraph)
                
                # parse the pos-tagged sentences into the dictionary format
                # example: {0: [('A', 'DT'), ('Study', 'NNP'), ('in', 'IN'), ('Temperament', 'NNP')]}
                pos_tagged_parsed = parse_pos(new_paragraph.sentences)
                
                ### {'study': {0}, 'temperament': {0}}
                text2sentence = text2cooc(pos_tagged_parsed)
                                
                closeness_list = generate_source(text2sentence, text + "_" + str(count))
                closeness.append(closeness_list)
                pickle.dump(text2sentence, open(paths.TOKEN_TO_SENTENCE_PATH + "/" \
                            + str(new_paragraph.paragraph_id) + text + ".t2s", "wb"))
            
            """
            format is:
            [ closenesses of paragraph
                [closeness of sentence in the paragraph]
            ]
            """
            pickle.dump(paragraph_list, open(paths.POS_PATH + "/" + text + ".p", "wb")) # used to be .pos
    pickle.dump(closeness, open(paths.CLOSENESS_PATH + "/" + "closeness.p", "wb")) # used to be .tsv            
            
if __name__ == "__main__":
    make_folders()
    extract_step()
    """
    april 3: looks good
    """