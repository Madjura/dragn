#  -*- coding: utf-8 -*-

from util import paths
def load_prov(name):
    with (open(paths.PARAGRAPH_CONTENT_PATH + "/" + name, "r", encoding="utf8")) as text:
        content = text.read()
    print(content)
    return content