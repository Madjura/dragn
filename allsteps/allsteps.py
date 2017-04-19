from extract.extract_step import extract_step, make_folders
from knowledge_base.knowledge_base_create_step import knowledge_base_create
from knowledge_base.knowledge_base_compute_step import knowledge_base_compute
from index.index_step import index_step

def all_steps():
    make_folders()
    extract_step()
    knowledge_base_create()
    knowledge_base_compute()
    index_step()