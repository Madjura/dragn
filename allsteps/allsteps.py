#!/usr/bin/env python3
"""Allows the execution of all steps in the dragn pipeline."""
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
from extract.extract_step import extract_step, make_folders
from index.index_step import index_step
from knowledge_base.knowledge_base_compute_step import knowledge_base_compute
from knowledge_base.knowledge_base_create_step import knowledge_base_create
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph
from query import querystep


def all_steps(texts, query=None, language="english", alias=None, task=None, alias_celery=None):
    """
    Performs all steps in the pipeline, up to and including query_step.

    :param texts: A list of texts to be processed.
    :param query: Optional. The query to be performed, if query_step execution is intended.
    :param language: Optional. Default: English. The language of the texts.
    :param alias: The Alias used for the text(s).
    :param task: Optional. Used when running the system with Celery to update the current state.
    :param alias_celery: Optional. Used to update the Alias status when using Celery.
    :return:
    """
    alias_object = alias
    if task:
        alias = "/" + alias
    else:
        alias = "/" + alias.identifier
    print("MAKING FOLDERS. This is very fast!")
    make_folders(alias=alias)
    if task:
        task.update_state(state="extract_step. Step 1/4")
    print("FOLDERS DONE, EXTRACT STEP")
    extract_step(texts=texts, language=language, alias=alias)
    if task:
        task.update_state(state="knowledge_base_create_step. Step 2/4.")
    print("EXTRACT STEP DONE, KB CREATE")
    if task:
        knowledge_base_create(alias=alias)
    print("KB CREATE DONE, KB COMPUTE")
    if task:
        task.update_state(state="knowledge_base_compute_step. Step 3/4. This step can take a long time!")
    knowledge_base_compute(alias=alias)
    print("KB COMPUTE DONE, INDEX")
    if task:
        task.update_state(state="index_step. Step 4/4.")
    index_step(alias=alias)
    print("INDEX DONE")
    if not task:
        alias_object.processed = True
        alias_object.save()
    else:
        alias_celery.processed = True
        alias_celery.save()
    if query:
        querystep.query(query)


def with_graphvizoutput(texts, query=None, language="english", alias=None):
    """
    Runs all_steps with GraphvizOutput, producing a call graph of all functions

    :param texts: A list of texts to be processed.
    :param query: Optional. The query to be performed, if query_step execution is intended.
    :param language: Optional. Default: English. The language of the texts.
    :param alias: The Alias used for the text(s).
    """
    graphviz = GraphvizOutput()
    graphviz.output_file = "allstep.png"
    with PyCallGraph(output=graphviz):
        all_steps(texts, query, language, alias)


# noinspection PyMethodMayBeStatic
class FakeAlias(object):
    """
    Used for running dragn without starting the Django server.
    Required because the Alias is stored in the database and not accessible properly without the server. This is used as
    a replacement and functions exactly as the normal Alias would, except it does not come from the database, neither
    is it stored there.
    """
    def __init__(self, identifier):
        self.identifier = identifier

    def save(self):
        """Blank method to bypass the Django database regarding the Alias System."""
        pass


if __name__ == "__main__":
    fake = FakeAlias("beast.txt,beyondthewall.txt,book.txt")
    all_steps(texts=["beast.txt", "beyondthewall.txt", "book.txt"], alias=fake)
    # with_graphvizoutput()
