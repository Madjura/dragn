from query.fuzzyset import FuzzySet
import pydot
import sys
from itertools import combinations
from math import log
import os
from util import paths
import gzip
from _collections import defaultdict
from graph import node
from graph.node import Node
from graph.edge import Edge
from graph.graph import Graph

class MemStoreQueryResult:
    """
    Wrapper for the result of a MemStore index query for an in-memory storage
    of the result content (terms, statements and relevant provenances),
    computation of various visualisations of the result and functions for
    abbreviated pretty printing and full XML and PDF storage of the result and
    its visualisation.
    """

    def __init__(self, name: str, tuid_set, queried=set(), fname_prefix='result-', \
                 visualization_parameters={}, min_w=0.5):
        """
        Constructor.
        Loads relevant data and prepares the visualization by setting parameters
        that will be used by Pydot.
        
            Args:
                name: The name of this object. Used when writing to disk.
                tuid_set: TODO
                queried: The query terms.
                    Default: Empty set.
                fname_prefix: The prefix for all files written to the disk from
                    this object.
                visualization_parameters: Optional dictionary to specify how the
                    Pydot graphs are going to look like.
                    If not specified, default parameters will be used.
        """
        
        # store index for generating the statements and provenances
        # the TUIDs that were queried for (for filtering the relevant statements)
        self.suid2stmt, self.tuid2suid = self.load_suid2stmt()
        self.queried = queried
        
        # result name and filenames for its storage
        self.name = name
        
        self.term_filename = fname_prefix + 'terms-' + self.name + '.xml'
        self.stmt_filename = fname_prefix + 'stmts-' + self.name + '.xml'
        self.prov_filename = fname_prefix + 'provs-' + self.name + '.xml'
        
        self.vis_filenames = {
          'TERMS' : fname_prefix + 'term_vis-' + self.name + '.png',
          'STMTS' : fname_prefix + 'stmt_vis-' + self.name + '.png',
          'PROVS' : fname_prefix + 'prov_vis-' + self.name + '.png',
          'TERMS_MAP' : fname_prefix + 'term_vis-' + self.name + '.map',
          'STMTS_MAP' : fname_prefix + 'stmt_vis-' + self.name + '.map',
          'PROVS_MAP' : fname_prefix + 'prov_vis-' + self.name + '.map',
          'TERMS_RAW' : fname_prefix + 'term_vis-' + self.name + '.dot',
          'STMTS_RAW' : fname_prefix + 'stmt_vis-' + self.name + '.dot',
          'PROVS_RAW' : fname_prefix + 'prov_vis-' + self.name + '.dot'
        }
        
        # result content
        self.tuid_set = tuid_set  # fuzzy term ID set, basis of the result
        
        ### minimum weight
        self.min_w = min_w
        
        # the result set cut according to the min_w parameter
        self.tuid_cut = FuzzySet()
        print("----INIT TUID SET LEN: ", len(self.tuid_set))
        print("MIN W", min_w)
        for tuid in self.tuid_set.cut(self.min_w):
            self.tuid_cut[tuid] = self.tuid_set[tuid]
        print("----INIT TUID CUT ", len(self.tuid_cut))
        
        self.suid_set = FuzzySet()  # fuzzy statement ID set
        self.puid_set = FuzzySet()  # fuzzy provenance ID set
        
        self.suid_dict = defaultdict(int)  # statement -> overall combined relevance weight
        self.tuid_dict = defaultdict(int)  # term -> combined weight based on connected statements
        self.puid_dict = defaultdict(int)  # provenance -> overall combined relevance weight
        self.prov_rels = defaultdict(float)  # edges between provenances and their weights
        
        #
        # Pydot stuff
        #
        self.visualization_dictionary = {  # pydot graphs for generating the visualisations
          'TERMS' : pydot.Dot('TERMS', graph_type='graph', size="1000"),
          'STMTS' : pydot.Dot('STMTS', graph_type='graph', size="1000"),
          'PROVS' : pydot.Dot('PROVS', graph_type='graph', size="1000")
        }
        self.vis_maps = {  # maps between visualisation node labels and names
          'TERMS' : [],
          'STMTS' : [],
          'PROVS' : []
        }
        
        # trying to get codes of relationships
        cooc_relcode = "close to"
        simr_relcode = "related to"

        if visualization_parameters:
            self.visualization_parameters = visualization_parameters
        else:
            # visualisation parameters
            self.visualization_parameters = {
              'PROG' : 'dot',  # graph rendering program
              'NODE_SHAPE' : 'rectangle',  # shape of the node
              'NODE_STYLE' : 'filled',  # style of the node
              'BASE_WIDTH' : 0.25,  # base width of the node in inches
              'FIXED_SIZE' : 'false',  # nodes are fixed/variable size
              'NCOL_MAP' : {  # colors of different node types
                'PROV_ART' : '#FFCC33',  # - article provenance
                'PROV_DAT' : '#FF9900',  # - data provenance
                'TERM_TRM' : '#6699CC',  # - term nodes in term results visualisation
                'TERM_STM' : '#6699CC'  # - term nodes in stmt results visualisation
              },
              'MAX_NLABLEN' : 50,  # maximum node label length (truncate longer)
              'MAX_ELABLEN' : 25,  # maximum edge label lentgh (truncate longer)
              'SCALE_BASE' : 10,  # log base for scaling node sizes
              'EDGE_COL' : {  # mapping of edge IDs to their colors
                cooc_relcode : 'blue',  # co-occurrence relation
                simr_relcode : 'red'  # similarity relation
              }
            }

    def load_suid2stmt(self):
        """
        # TODO: write up what this is
        """
        
        suid2stmt = {}
        tuid2suid = {}
        path = os.path.join(paths.SUIDS_PATH_EXPERIMENTAL, "suids.tsv.gz")
        if os.path.exists(path):
            with gzip.open(path, "rb") as f:
                for line in f.read().decode().split("\n"):
                    spl = line.split("\t")
                    if len(spl) != 5:
                        continue
                    # updating the statement ID -> statement mapping
                    try:
                        suid = int(spl[0])
                    except ValueError:
                        suid = spl[0]
                    statement = (spl[1], spl[2], spl[3], float(spl[4]))
                    suid2stmt[suid] = statement
                    # updating the term ID -> statement ID mapping record for the subject
                    if not statement[0] in tuid2suid:
                        tuid2suid[statement[0]] = []
                    tuid2suid[statement[0]].append(suid)
                    # updating the term ID -> statement ID mapping record for the object
                    if not statement[2] in tuid2suid:
                        tuid2suid[statement[2]] = []
                    tuid2suid[statement[2]].append(suid)
                f.close()
        else:
            sys.stderr.write('\nW @ MemStoreIndex() - suids cannot be loaded!\n')
        return suid2stmt, tuid2suid

    def load_suid2prov(self):
        suid2prov = defaultdict(lambda: list())
        if os.path.exists(os.path.join(paths.INDEX_PATH_EXPERIMENTAL, 'provenances.tsv.gz')):
            fn = os.path.join(paths.INDEX_PATH_EXPERIMENTAL, 'provenances.tsv.gz')
            f = gzip.open(fn, 'rb')
            for line in f.read().decode().split('\n'):
                spl = line.split('\t')
                if len(spl) != 3:
                    print("INVALID LENGTH")
                    continue
                key, value = spl[0], (spl[1], float(spl[2]))
                suid2prov[key].append(value)
            f.close()
        else:
            sys.stderr.write('\nW @ MemStoreIndex() - prov. cannot be loaded!\n')
        return suid2prov

    def populate_dictionaries(self):
        # populates the statement and provenance relevance dictionaries

        ### THIS HAS ONLY RELATED_TO STUFF. NOT close to
        ### generated in gen_sim_suid2puid_exp
        suid2prov = self.load_suid2prov()
        ### his tuid cut: FuzzySet: [(768, 0.49839683762576953),
        for tuid in self.tuid_cut:
            # the degree of membership of the term in the result
            tuid_weight = self.tuid_cut[tuid]
            
            ### his tuid2suid dict: {0: [73, 163, 297, 382, 409, 427, 504, 586, 617, 663,
            for suid in self.tuid2suid[tuid]:
                # original statement
                
                ### his suid2sttmt dict: {0: (304, 1, 170, 0.24094163517471326), 1: (981, 1, 972, 0.39100798646527024),
                try:
                    s, _p, o, suid_weight = self.suid2stmt[suid]
                except KeyError:
                    print("KEYERROR")
                    continue ### TODO: investigate why this happens
                if not (s in self.queried or o in self.queried):
                    # don't process statements that are not related to the queried terms
                    continue
                # updating the result statement dict with the combined tuid/suid weight
                self.suid_dict[suid] += tuid_weight * suid_weight
                # updating the term weight based on statements connected to it
                self.tuid_dict[tuid] += self.suid_dict[suid]
                # adding also the statement subject and object to the dictionary
                if s != tuid:
                    self.tuid_dict[s] += self.suid_dict[suid]
                if o != tuid:
                    self.tuid_dict[o] += self.suid_dict[suid]
                # updating the result provenance dict with the combined tuid/suid/puid
                # weight
                
                for puid, puid_weight in suid2prov[suid]:
                    self.puid_dict[puid] += tuid_weight * suid_weight * puid_weight
                # updating the self.prov_rels dictionary
                for (puid1, w1), (puid2, w2) in combinations(suid2prov[suid], 2):
                    # aggregate value for the provenance-provenance relation
                    w = tuid_weight * suid_weight * (w1 + w2) / 2
                    self.prov_rels[(puid2, puid1)] += w
        # generating the statement and provenance result fuzzy sets from the
        # dictionaries
        self.suid_set = self._generate_fuzzy_set(self.suid_dict)
        print("SUID DICT LENGTH OLD: ", len(self.suid_dict))
        print("SUID SET LENGTH OLD: ", len(self.suid_set))
        self.puid_set = self._generate_fuzzy_set(self.puid_dict)
        print("PUID DICT LENGTH OLD: ", len(self.puid_dict))
        print("PUID SET LENGTH OLD: ", len(self.puid_set))
    
    def _generate_fuzzy_set(self, dct, agg=max):
        # generates a fuzzy set from a member->weight dictionary, normalising the
        # weight values first by a constant computed by the supplied agg function
        # from the dictionary values (maximum by default)

        fset = FuzzySet()
        if len(dct) == 0:
            return fset
        norm_const = agg(list(dct.values()))
        if norm_const <= 0:
            # making sure it's OK to divide by it meaningfully
            norm_const = 1.0
        for member, weight in list(dct.items()):
            # cutting off the values out of [0,1] interval
            w = float(weight) / norm_const
            if w > 1:
                w = 1
            if w < 0:
                w = 0
            fset[member] = w
        return fset
    
    def generate_visualisations(self, max_n=50, max_e=250):
        # generate visualisations from the populated results
        self._gen_term_vis(self.visualization_dictionary['TERMS'], max_n, max_e)
        return self._gen_stmt_vis(self.visualization_dictionary['STMTS'], max_n, max_e)
        self._gen_prov_vis(self.visualization_dictionary['PROVS'], max_n, max_e)
                
### CHECK GRAPH
    def _gen_term_vis(self, graph: pydot.Dot, max_nodes: int, max_edges: int):
        # generate the term-based visualisation of the results (up to max_nodes
        # most relevant nodes in the graph)
        # if lex_labels is True, the true lexical labels are used for the nodes,
        # otherwise numbers are being used

        # getting the relevant terms
        ### these are terms/expressions: ["cry", "stay", ...]
        tuids = [x[0] for x in self.tuid_cut.sort(reverse=True, limit=max_nodes)]
        
        
        # getting the scale factors for the size of each term node
        tuid2scale = dict([(x, self.tuid_dict[x]) for x in tuids])
        norm_const = 1.0
        if len(tuid2scale):
            norm_const = min(tuid2scale.values())
        for tuid in tuid2scale:
            tuid2scale[tuid] /= norm_const
            
            
        # constructing the graph nodes
        nodes = {}
        for index, tuid in enumerate(tuids):
            # setting the node label -> node name mapping
            node_name = tuid
            node_label = str(index)
            self.vis_maps['TERMS'].append((node_label, node_name))
            
            # setting the node size and deriving the fontsize from it
            ### the 1.0 is originally a scaled factor based on the tuid weight value
            node_width = log(self.visualization_parameters['BASE_WIDTH'] * 1.0, self.visualization_parameters['SCALE_BASE'])
            # enforcing a minimal size of the scaled nodes
            if node_width < 0.4:
                node_width = 0.4
            font_size = int(24 * node_width)  # 1/3 of the node, 72 points per inch
            # setting the node colour
            node_col = self.visualization_parameters['NCOL_MAP']['TERM_TRM']
            
            # used to trunctuate if name too long
            label = node_name[:self.visualization_parameters['MAX_NLABLEN']]
            
            # creating the node
            nodes[tuid] = pydot.Node(\
              label, \
              style = self.visualization_parameters['NODE_STYLE'], \
              fillcolor = node_col, \
              shape = self.visualization_parameters['NODE_SHAPE'], \
              width = str(node_width), \
              fontsize = str(font_size), \
              fixedsize = self.visualization_parameters['FIXED_SIZE']\
            )
        # adding the graph nodes to the TERMS visualisation
        for node in list(nodes.values()):
            self.visualization_dictionary['TERMS'].add_node(node)
        # constructing the edges (limited by max_edges)
        suid_list = list(self.suid_set.items())
        num_edges =  0
        suid_list.sort(key=lambda x: x[1], reverse=True)
        for suid, w in suid_list:
            if num_edges > max_edges:
                print("MAX EDGES")
                break
            s, p, o, _corp_w = self.suid2stmt[suid]
            # adding the edge if both arguments are present in the node set
            if s in nodes and o in nodes:
                # edge label, if different from related_to, observed_with (those are
                # distinguished by the red and blue colours, respectively)
                edge_label = ''
                if p not in self.visualization_parameters['EDGE_COL']:
                    # non-default edge type, add a specific label
                    edge_label = p
                edge_label = edge_label[:self.visualization_parameters['MAX_ELABLEN']]
                # edge = pydot.Edge(nodes[s],nodes[o],label=edge_label)
                edge_col = 'black'  # default colour
                if p in self.visualization_parameters['EDGE_COL']:
                    edge_col = self.visualization_parameters['EDGE_COL'][p]
                edge_wgh = str(int(w * 10000))
                edge = None
                if len(edge_label):
                    edge = pydot.Edge(nodes[s],
                                      nodes[o],
                                      color=edge_col,
                                      weight=edge_wgh, \
                      label=edge_label)
                else:
                    edge = pydot.Edge(nodes[s],
                                      nodes[o],
                                      color=edge_col,
                                      weight=edge_wgh)
                self.visualization_dictionary['TERMS'].add_edge(edge)
                num_edges += 1
    
    def generate_statement_nodes(self, max_nodes):
        # getting the relevant term IDs
        tuid_list = list(self.tuid_dict.items())
        tuid_list.sort(key=lambda x: x[1], reverse=True)
        tuids = [x[0] for x in tuid_list[:max_nodes]]
        # getting the scale factors for the size of each term node
        tuid2scale = dict([(x, self.tuid_dict[x]) for x in tuids])
        norm_const = 1.0
        if len(tuid2scale):
            norm_const = min(tuid2scale.values())
        for tuid in tuid2scale:
            tuid2scale[tuid] /= norm_const
        # constructing the graph nodes
        nodes = {}
        i = 0
        graph_nodes = {}
        for tuid in tuids:
            # setting the node label -> node name mapping
            node_name = tuid
            node_label = str(i)
            self.vis_maps['STMTS'].append((node_label, node_name))
            # setting the node size and deriving the fontsize from it
            node_width = log(self.visualization_parameters['BASE_WIDTH'] * tuid2scale[tuid], \
              self.visualization_parameters['SCALE_BASE'])
            # enforcing a minimal size of the scaled nodes
            if node_width < 0.4:
                node_width = 0.4
            font_size = int(24 * node_width)  # 1/3 of the node, 72 points per inch
            # setting the node colour
            node_col = self.visualization_parameters['NCOL_MAP']['TERM_STM']
            # setting the node label either to the lexical name or to an ID
            label = node_name[:self.visualization_parameters['MAX_NLABLEN']]
            # creating the node
            nodes[tuid] = pydot.Node(\
              label, \
              style=self.visualization_parameters['NODE_STYLE'], \
              fillcolor=node_col, \
              shape=self.visualization_parameters['NODE_SHAPE'], \
              width=str(node_width), \
              fontsize=str(font_size), \
              fixedsize=self.visualization_parameters['FIXED_SIZE']\
            )
            if tuid in self.queried:
                node_col = "green"
            graph_nodes[tuid] = Node(name=tuid, color=node_col, 
                                     width=node_width, label_size=font_size)
            i += 1
        # adding the graph nodes to the TERMS visualisation
        for node in list(nodes.values()):
            self.visualization_dictionary['STMTS'].add_node(node)
        return nodes, graph_nodes
            
    def _gen_stmt_vis(self, graph: pydot.Dot, max_nodes: int, max_edges: int):
        # generate the more statement oriented visualisation of the results (up to
        # max_nodes most relevant statement nodes in the graph), similarly to the
        # term visualisation, however, this time including all terms from the
        # result statements, not only the terms in the term-result set
        # if lex_labels is True, the true lexical labels are used for the nodes,
        # otherwise numbers are being used
        
        nodes, graph_nodes = self.generate_statement_nodes(max_nodes)
        # constructing the edges (limited by max_edges)
        tuid_list, num_edges = list(self.suid_set.items()), 0
        tuid_list.sort(key=lambda x: x[1], reverse=True)
        for suid, w in tuid_list:
            if num_edges > max_edges:
                break
            s, p, o, _corp_w = self.suid2stmt[suid]
            # adding the edge if both arguments are present in the node set
            if s in nodes and o in nodes:
                # edge label, if different from related_to, observed_with (those are
                # distinguished by the red and blue colours, respectively)
                edge_label = ''
                if p not in self.visualization_parameters['EDGE_COL']:
                    # non-default edge type, add a specific label
                    edge_label = p
                edge_label = edge_label[:self.visualization_parameters['MAX_ELABLEN']]
                # edge = pydot.Edge(nodes[s],nodes[o],label=edge_label)
                edge_col = 'black'  # default colour
                if p in self.visualization_parameters['EDGE_COL']:
                    edge_col = self.visualization_parameters['EDGE_COL'][p]
                edge_wgh = str(int(w * 10000))
                edge = None
                if len(edge_label):
                    edge = pydot.Edge(nodes[s], nodes[o], color=edge_col, weight=edge_wgh, \
                      label=edge_label)
                else:
                    edge = pydot.Edge(nodes[s], nodes[o], color=edge_col, weight=edge_wgh)
                self.visualization_dictionary['STMTS'].add_edge(edge)
                graph_edge = Edge(graph_nodes[s], graph_nodes[o], color=edge_col)
                graph_nodes[s].add_edge_object(graph_edge)
                num_edges += 1
                
        return Graph(graph_nodes.values())
        # print 'DEBUG -- number of STMTS graph nodes:', \
        #  len(self.visualization_dictionary['STMTS'].get_node_list())
        # print 'DEBUG -- number of TERMS graph edges:', \
        #  len(self.visualization_dictionary['STMTS'].get_edge_list())

    def _gen_prov_vis(self, graph: pydot.Dot, max_nodes: int, max_edges):
        # generate the provenance-based visualisation of the results (up to
        # max_nodes most relevant nodes in the graph)
        # if lex_labels is True, the true lexical labels are used for the nodes,
        # otherwise numbers are being used

        # getting the relevant provenance IDs
        puids = [x[0] for x in self.puid_set.sort(reverse=True, limit=max_nodes)]
        # getting the scale factors for the size of each term node
        puid2scale = dict([(x, self.puid_dict[x]) for x in puids])
        norm_const = 1.0
        if len(puid2scale):
            norm_const = min(puid2scale.values())
        for puid in puid2scale:
            puid2scale[puid] /= norm_const
        # constructing the graph nodes
        nodes, i = {}, 0
        for puid in puids:
            # setting the node label -> node name mapping
            node_name = puid
            node_label = str(i)
            node_title = ''
            self.vis_maps['PROVS'].append((node_label, node_name, node_title))
            # setting the node size and deriving the fontsize from it
            node_width = log(self.visualization_parameters['BASE_WIDTH'] * puid2scale[puid], \
              self.visualization_parameters['SCALE_BASE'])
            # enforcing a minimal size of the scaled nodes
            if node_width < 0.4:
                node_width = 0.4
            font_size = int(24 * node_width)  # 1/3 of the node, 72 points per inch
            # setting the node colour - distinguish between data and article
            # provenance by the fact that article provenance label is numeric,
            # while the data provenance is not
            node_col = self.visualization_parameters['NCOL_MAP']['PROV_ART']
            if not node_name.split('_')[0].isdigit():
                node_col = self.visualization_parameters['NCOL_MAP']['PROV_DAT']
            # print 'DEBUG -- provenance node name:', node_name
            # print 'DEBUG -- setting the provenance node colour to:', node_col
            # setting the node label either to the lexical name or to an ID
            label = node_name[:self.visualization_parameters['MAX_NLABLEN']]
            # creating the node
            nodes[puid] = pydot.Node(\
              label, \
              style=self.visualization_parameters['NODE_STYLE'], \
              fillcolor=node_col, \
              shape=self.visualization_parameters['NODE_SHAPE'], \
              width=str(node_width), \
              fontsize=str(font_size), \
              fixedsize=self.visualization_parameters['FIXED_SIZE']\
            )
            i += 1
        # adding the graph nodes to the PROVS visualisation
        for node in list(nodes.values()):
            self.visualization_dictionary['PROVS'].add_node(node)
        # computing normalised edge weights
        prov_rels_set = self._generate_fuzzy_set(self.prov_rels)
        # constructing the edges (limited by max_edge)
        l, num_edges = list(prov_rels_set.items()), 0
        l.sort(key=lambda x: x[1], reverse=True)
        for (puid1, puid2), w in l:
            if num_edges > max_edges:
                break
            if puid1 in nodes and puid2 in nodes:
                # adding the edge if both provenances are relevant nodes
                # label too messy, but may be added again
                # edge_label = \
                #  str(prov_rels_set[(puid1,puid2)])[:self.visualization_parameters['MAX_ELABLEN']]
                # edge = pydot.Edge(nodes[puid1],nodes[puid2],label=edge_label)
                edge_wgh = str(int(w * 10000))
                edge = pydot.Edge(nodes[puid1], nodes[puid2], weight=edge_wgh)
                self.visualization_dictionary['PROVS'].add_edge(edge)
                num_edges += 1
    
    def pretty_print(self, limit=10) -> [str]:
        """
        Returns and prints the most relevant terms for the given query, the most
        relevant statements and the most relevant sources.
        
            Args:
                limit: How many elements are to be returned. 
                    Default: 10, for the top ten.
                    
            Returns:
                A list of strings, formatted to nicely display the result.
        """
        
        # prepare a pretty print string with an abbreviated version of the result
        # (up to limit items from term, statement and provenance sets)

        lines = [str(limit) + ' MOST RELEVANT TERMS:']
        i = 0
        for tuid, w in self.tuid_cut.sort(reverse=True, limit=limit):
            i += 1
            lines.append('RANK ' + str(i) + '.')
            lines.append('  * term  : ' + tuid)
            lines.append('  * weight: ' + str(w))
        lines += [str(limit) + ' MOST RELEVANT STATEMENTS:']
        i = 0
        for suid, w in self.suid_set.sort(reverse=True, limit=limit):
            i += 1
            s, p, o, _corp_w = self.suid2stmt[suid]
            lines.append('RANK ' + str(i) + '.')
            lines.append('  * argument: ' + s)
            lines.append('  * relation: ' + p)
            lines.append('  * argument: ' + o)
            lines.append('  * weight  : ' + str(w))
        lines += [str(limit) + ' MOST RELEVANT PROVENANCE SOURCES:']
        i = 0
        for puid, w in self.puid_set.sort(reverse=True, limit=limit):
            i += 1
            prov_meta = {}
            if puid in self.index.puid2meta:
                prov_meta = 0.5
                #prov_meta = self.index.puid2meta[puid]
            lines.append('RANK ' + str(i) + '.')
            for key, value in list(prov_meta.items()):
                lines.append('  * ' + str(key) + ': ' + str(value.encode('utf-8')))  # ,\
                #  errors='replace')))
            lines.append('  * weight  : ' + str(w))
        return '\n'.join(lines)