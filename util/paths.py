MAIN_FOLDER = "../data"

# Path to where the texts are placed
TEXT_PATH = MAIN_FOLDER + "/texts"

# Path to where the paragraph files will be placed
PARAGRAPHS_PATH = MAIN_FOLDER + "/paragraphs"

# Path to where the POS tagged text / sentence chunks are
POS_PATH = MAIN_FOLDER + "/pos"

# Path to the token -> sentence id mapping
TOKEN_TO_SENTENCE_PATH = MAIN_FOLDER + "/term2sentence"

# Path the closeness file
# Pickled list of a list of Closeness objects
CLOSENESS_PATH = MAIN_FOLDER + "/closeness"

MEMSTORE_PATH_EXPERIMENTAL = MAIN_FOLDER + "/memstoreexperimental"

SUIDS_PATH_EXPERIMENTAL = MAIN_FOLDER + "/suidsexperimental"

INDEX_PATH_EXPERIMENTAL = MAIN_FOLDER + "/indexexperimental"

EXPRESSION_SET_PATH_EXPERIMENTAL = MAIN_FOLDER + "/expressionsexperimental"

RELATIONS_PATH = MAIN_FOLDER + "/relations"

RELATION_EXPRESSIONS_PATH = MAIN_FOLDER + "/relations/expressions"

RELATION_PROVENANCES_PATH = MAIN_FOLDER + "/relations/provenances"

ALL = [
    MAIN_FOLDER,
    TEXT_PATH,
    PARAGRAPHS_PATH,
    POS_PATH,
    TOKEN_TO_SENTENCE_PATH,
    CLOSENESS_PATH,
    MEMSTORE_PATH_EXPERIMENTAL,
    SUIDS_PATH_EXPERIMENTAL,
    INDEX_PATH_EXPERIMENTAL,
    EXPRESSION_SET_PATH_EXPERIMENTAL,
    RELATIONS_PATH,
    RELATION_EXPRESSIONS_PATH,
    RELATION_PROVENANCES_PATH
    ]