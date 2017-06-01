from extract.extract_step import extract_step, make_folders
from index.index_step import index_step
from knowledge_base.knowledge_base_compute_step import knowledge_base_compute
from knowledge_base.knowledge_base_create_step import knowledge_base_create


def all_steps():
    print("MAKING FOLDERS")
    make_folders()
    print("FOLDERS DONE, EXTRACT STEP")
    extract_step()
    print("EXTRACT STEP DONE, KB CREATE")
    knowledge_base_create()
    print("KB CREATE DONE, KB COMPUTE")
    knowledge_base_compute()
    print("KB COMPUTE DONE, INDEX")
    index_step()
    print("INDEX DONE")


if __name__ == "__main__":
    all_steps()
