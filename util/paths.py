"""
All the paths used by the system to write various files to.
Recommended to use absolute paths for everything, but not required.
"""
MAIN_FOLDER = "../data"

# Path to where the texts are placed
TEXT_PATH = "E:\workspace\dragn\data\\texts"

# Path to where metainformation about the text files is being stored
TEXT_META_PATH = MAIN_FOLDER + "/texts/meta"

# Path to the toplevel directory for paragraph contents
PARAGRAPHS_PATH = MAIN_FOLDER + "/paragraphs"

# Path to the directory where the contents of the paragraphs (the text) are being stored
PARAGRAPH_CONTENT_PATH = "E:\workspace\data\paragraphs\contents"

# Path to where the POS tagged text / sentence chunks are
POS_PATH = MAIN_FOLDER + "/pos"

# Path to where the files with the information about the weighted distances are
CLOSENESS_PATH = "E:\workspace\data\closeness"

# Path to where the memstore is stored
MEMSTORE_PATH = "E:\\workspace\\data\\memstoreexperimental\\"

# Path to where the shortform relations are stored
RELATION_WEIGHT_PATH = "E:\\workspace\\data\\expressionsexperimental"

# Path to where the mapping of token: relations is being stored
RELATIONS_PATH = "E:\\workspace\data\\relations"

# Path to where the SPOP tuples are stored
RELATION_PROVENANCES_PATH = "E:\\workspace\\data\\relations\\provenances"

ALL = [
    MAIN_FOLDER,
    TEXT_PATH,
    TEXT_META_PATH,
    PARAGRAPHS_PATH,
    PARAGRAPH_CONTENT_PATH,
    POS_PATH,
    CLOSENESS_PATH,
    MEMSTORE_PATH,
    RELATION_WEIGHT_PATH,
    RELATIONS_PATH,
    RELATION_PROVENANCES_PATH
]

EXCLUDE = [
    MAIN_FOLDER,
    PARAGRAPHS_PATH,
    TEXT_PATH
]