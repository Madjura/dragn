"""
All the paths used by the system to write various files to.
Recommended to use absolute paths for everything, but not required.
"""
__copyright__ = """
Copyright (C) 2017 Thomas Huber <huber150@stud.uni-passau.de, madjura@gmail.com>
Copyright (C) 2012 Vit Novacek (vit.novacek@deri.org), Digital Enterprise
Research Institute (DERI), National University of Ireland Galway (NUIG)
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
