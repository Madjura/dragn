from query_step.fuzzyset import FuzzySet
import pydot
import sys
from itertools import combinations
from math import log
import os
from util import paths
import gzip
from _collections import defaultdict
class MemStoreQueryResult:
    """
    Wrapper for the result of a MemStore index query for an in-memory storage
    of the result content (terms, statements and relevant provenances),
    computation of various visualisations of the result and functions for
    abbreviated pretty printing and full XML and PDF storage of the result and
    its visualisation.
    """

    def __init__(self, name, tuid_set, queried=set(), fname_prefix='result-', \
    vis_par={}, min_w=0.5):
        # store index for generating the statements and provenances
        # the TUIDs that were queried for (for filtering the relevant statements)
        self.suid2stmt, self.tuid2suid = self.load_suid2stmt()
        self.queried = queried
        # result name and filenames for its storage
        self.name = name
        self.fname_prefix = fname_prefix
        self.term_filename = self.fname_prefix + 'terms-' + self.name + '.xml'
        self.stmt_filename = self.fname_prefix + 'stmts-' + self.name + '.xml'
        self.prov_filename = self.fname_prefix + 'provs-' + self.name + '.xml'
        self.vis_filenames = {
          'TERMS' : self.fname_prefix + 'term_vis-' + self.name + '.png',
          'STMTS' : self.fname_prefix + 'stmt_vis-' + self.name + '.png',
          'PROVS' : self.fname_prefix + 'prov_vis-' + self.name + '.png',
          'TERMS_MAP' : self.fname_prefix + 'term_vis-' + self.name + '.map',
          'STMTS_MAP' : self.fname_prefix + 'stmt_vis-' + self.name + '.map',
          'PROVS_MAP' : self.fname_prefix + 'prov_vis-' + self.name + '.map',
          'TERMS_RAW' : self.fname_prefix + 'term_vis-' + self.name + '.dot',
          'STMTS_RAW' : self.fname_prefix + 'stmt_vis-' + self.name + '.dot',
          'PROVS_RAW' : self.fname_prefix + 'prov_vis-' + self.name + '.dot'
        }
        # result content
        ### FuzzySet: [(4, 0.0004664468423382175), 
        self.tuid_set = tuid_set  # fuzzy term ID set, basis of the result
        self.min_w = min_w
        # the result set cut according to the min_w parameter
        self.tuid_cut = FuzzySet()
        for tuid in self.tuid_set.cut(self.min_w):
            self.tuid_cut[tuid] = self.tuid_set[tuid]
        self.suid_set = FuzzySet()  # fuzzy statement ID set
        self.puid_set = FuzzySet()  # fuzzy provenance ID set
        self.suid_dict = defaultdict(int)  # statement -> overall combined relevance weight
        self.tuid_dict = defaultdict(int)  # term -> combined weight based on connected statements
        self.puid_dict = defaultdict(int)  # provenance -> overall combined relevance weight
        self.prov_rels = defaultdict(float)  # edges between provenances and their weights
        self.vis_dict = {  # pydot graphs for generating the visualisations
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
        cooc_relcode, simr_relcode = -2, -1
        try:
            cooc_relcode = "related to"
        except KeyError:
            sys.stderr.write('\nW@ifce.py - no co-occurrence relation present\n')
        try:
            simr_relcode = "related to"
        except KeyError:
            sys.stderr.write('\nW@ifce.py - no similarity relation present\n')
        # visualisation parameters
        self.vis_par = {
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
        if vis_par != {}:
            self.vis_par = vis_par

    def load_suid2stmt(self):
        suid2stmt, tuid2suid = {}, {}
        if os.path.exists(os.path.join(paths.SUIDS_PATH_EXPERIMENTAL, 'suids.tsv.gz')):
            fn = os.path.join(paths.SUIDS_PATH_EXPERIMENTAL, 'suids.tsv.gz')
            f = gzip.open(fn, 'rb')
            for line in f.read().decode().split('\n'):
                spl = line.split('\t')
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

        # print 'DEBUG -- number of all result terms     :', len(self.tuid_set)
        # print 'DEBUG -- minimum result weight threshold:', self.min_w
        # print 'DEBUG -- number of filtered result terms:', len(self.tuid_cut)
        i = 0
        suid2prov = self.load_suid2prov()
        
        ### his tuid cut: FuzzySet: [(768, 0.49839683762576953),
        for tuid in self.tuid_cut:
            i += 1
            # print 'DEBUG -- processing result term:', self.index.lexicon[tuid]
            # print '  *', i, 'out of', len(self.tuid_cut)
            # print '  * weight:', self.tuid_cut[tuid]
            # print '  * candidate rel. statements:', len(self.index.tuid2suid[tuid])
            # the degree of membership of the term in the result
            tuid_weight = self.tuid_cut[tuid]
            rel_suid = 0
            
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
                rel_suid += 1
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
                
                ### ENTRYPOINT 21 march - INVESTIGATE KEY ERROR
                for puid, puid_weight in suid2prov[suid]:
                    self.puid_dict[puid] += tuid_weight * suid_weight * puid_weight
                # updating the self.prov_rels dictionary
                for (puid1, w1), (puid2, w2) in combinations(suid2prov[suid], 2):
                    # aggregate value for the provenance-provenance relation
                    w = tuid_weight * suid_weight * (w1 + w2) / 2
                    self.prov_rels[(puid2, puid1)] += w
            # print '  * actual rel. statements:', rel_suid
        # generating the statement and provenance result fuzzy sets from the
        # dictionaries
        self.suid_set = self._generate_fuzzy_set(self.suid_dict)
        self.puid_set = self._generate_fuzzy_set(self.puid_dict)
        print("foo")

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

    def generate_visualisations(self, tuid_dict, max_n=50, max_e=250):
        # generate visualisations from the populated results

        self._gen_term_vis(self.vis_dict['TERMS'], max_n, max_e, tuid_dict)
        self._gen_stmt_vis(self.vis_dict['STMTS'], max_n, max_e, tuid_dict)
        self._gen_prov_vis(self.vis_dict['PROVS'], max_n, max_e, tuid_dict)

### CHECK GRAPH
    def _gen_term_vis(self, graph, max_nodes, max_edges, tuid_dict, lex_labels=True):
        # generate the term-based visualisation of the results (up to max_nodes
        # most relevant nodes in the graph)
        # if lex_labels is True, the true lexical labels are used for the nodes,
        # otherwise numbers are being used

        # getting the relevant term IDs
        tuids = [x[0] for x in self.tuid_cut.sort(reverse=True, limit=max_nodes)]
        # getting the scale factors for the size of each term node
        #======================================================================
        # tuid2scale = dict([(x, tuid_dict[x]) for x in tuids])
        # norm_const = 1.0
        #======================================================================
        #======================================================================
        # if len(tuid2scale):
        #     norm_const = min(tuid2scale.values())
        # for tuid in tuid2scale:
        #     tuid2scale[tuid] /= norm_const
        #======================================================================
        # constructing the graph nodes
        nodes, i = {}, 0
        for tuid in tuids:
            # setting the node label -> node name mapping
            node_name = tuid
            node_label = str(i)
            self.vis_maps['TERMS'].append((node_label, node_name))
            # setting the node size and deriving the fontsize from it
            node_width = log(self.vis_par['BASE_WIDTH'] * 1.0, \
              self.vis_par['SCALE_BASE'])
            # enforcing a minimal size of the scaled nodes
            if node_width < 0.4:
                node_width = 0.4
            font_size = int(24 * node_width)  # 1/3 of the node, 72 points per inch
            # setting the node colour
            node_col = self.vis_par['NCOL_MAP']['TERM_TRM']
            # setting the node label either to the lexical name or to an ID
            label = node_label
            if lex_labels:
                label = node_name[:self.vis_par['MAX_NLABLEN']]
            # creating the node
            nodes[tuid] = pydot.Node(\
              label, \
              style=self.vis_par['NODE_STYLE'], \
              fillcolor=node_col, \
              shape=self.vis_par['NODE_SHAPE'], \
              width=str(node_width), \
              fontsize=str(font_size), \
              fixedsize=self.vis_par['FIXED_SIZE']\
            )
            i += 1
        # adding the graph nodes to the TERMS visualisation
        for node in list(nodes.values()):
            self.vis_dict['TERMS'].add_node(node)
        # constructing the edges (limited by max_edges)
        l, num_edges = list(self.suid_set.items()) , 0
        l.sort(key=lambda x: x[1], reverse=True)
        for suid, w in l:
            if num_edges > max_edges:
                print("MAX EDGES")
                break
            s, p, o, _corp_w = self.suid2stmt[suid]
            # adding the edge if both arguments are present in the node set
            if s in nodes and o in nodes:
                # edge label, if different from related_to, observed_with (those are
                # distinguished by the red and blue colours, respectively)
                edge_label = ''
                if p not in self.vis_par['EDGE_COL']:
                    # non-default edge type, add a specific label
                    edge_label = p
                edge_label = edge_label[:self.vis_par['MAX_ELABLEN']]
                # edge = pydot.Edge(nodes[s],nodes[o],label=edge_label)
                edge_col = 'black'  # default colour
                if p in self.vis_par['EDGE_COL']:
                    edge_col = self.vis_par['EDGE_COL'][p]
                edge_wgh = str(int(w * 10000))
                edge = None
                if len(edge_label):
                    edge = pydot.Edge(nodes[s], nodes[o], color=edge_col, weight=edge_wgh, \
                      label=edge_label)
                else:
                    edge = pydot.Edge(nodes[s], nodes[o], color=edge_col, weight=edge_wgh)
                self.vis_dict['TERMS'].add_edge(edge)
                num_edges += 1
        # print 'DEBUG -- number of TERMS graph nodes:', \
        #  len(self.vis_dict['TERMS'].get_node_list())
        # print 'DEBUG -- number of TERMS graph edges:', \
        #  len(self.vis_dict['TERMS'].get_edge_list())

    def _gen_stmt_vis(self, graph, max_nodes, max_edges, lex_labels=True):
        # generate the more statement oriented visualisation of the results (up to
        # max_nodes most relevant statement nodes in the graph), similarly to the
        # term visualisation, however, this time including all terms from the
        # result statements, not only the terms in the term-result set
        # if lex_labels is True, the true lexical labels are used for the nodes,
        # otherwise numbers are being used

        # getting the relevant term IDs
        l = list(self.tuid_dict.items())
        l.sort(key=lambda x: x[1], reverse=True)
        tuids = [x[0] for x in l[:max_nodes]]
        # getting the scale factors for the size of each term node
        tuid2scale = dict([(x, self.tuid_dict[x]) for x in tuids])
        norm_const = 1.0
        if len(tuid2scale):
            norm_const = min(tuid2scale.values())
        for tuid in tuid2scale:
            tuid2scale[tuid] /= norm_const
        # constructing the graph nodes
        nodes, i = {}, 0
        for tuid in tuids:
            # setting the node label -> node name mapping
            node_name = tuid
            node_label = str(i)
            self.vis_maps['STMTS'].append((node_label, node_name))
            # setting the node size and deriving the fontsize from it
            node_width = log(self.vis_par['BASE_WIDTH'] * tuid2scale[tuid], \
              self.vis_par['SCALE_BASE'])
            # enforcing a minimal size of the scaled nodes
            if node_width < 0.4:
                node_width = 0.4
            font_size = int(24 * node_width)  # 1/3 of the node, 72 points per inch
            # setting the node colour
            node_col = self.vis_par['NCOL_MAP']['TERM_STM']
            # setting the node label either to the lexical name or to an ID
            label = node_label
            if lex_labels:
                label = node_name[:self.vis_par['MAX_NLABLEN']]
            # creating the node
            nodes[tuid] = pydot.Node(\
              label, \
              style=self.vis_par['NODE_STYLE'], \
              fillcolor=node_col, \
              shape=self.vis_par['NODE_SHAPE'], \
              width=str(node_width), \
              fontsize=str(font_size), \
              fixedsize=self.vis_par['FIXED_SIZE']\
            )
            i += 1
        # adding the graph nodes to the TERMS visualisation
        for node in list(nodes.values()):
            self.vis_dict['STMTS'].add_node(node)
        # constructing the edges (limited by max_edges)
        l, num_edges = list(self.suid_set.items()), 0
        l.sort(key=lambda x: x[1], reverse=True)
        for suid, w in l:
            if num_edges > max_edges:
                break
            s, p, o, _corp_w = self.suid2stmt[suid]
            # adding the edge if both arguments are present in the node set
            if s in nodes and o in nodes:
                # edge label, if different from related_to, observed_with (those are
                # distinguished by the red and blue colours, respectively)
                edge_label = ''
                if p not in self.vis_par['EDGE_COL']:
                    # non-default edge type, add a specific label
                    edge_label = p
                edge_label = edge_label[:self.vis_par['MAX_ELABLEN']]
                # edge = pydot.Edge(nodes[s],nodes[o],label=edge_label)
                edge_col = 'black'  # default colour
                if p in self.vis_par['EDGE_COL']:
                    edge_col = self.vis_par['EDGE_COL'][p]
                edge_wgh = str(int(w * 10000))
                edge = None
                if len(edge_label):
                    edge = pydot.Edge(nodes[s], nodes[o], color=edge_col, weight=edge_wgh, \
                      label=edge_label)
                else:
                    edge = pydot.Edge(nodes[s], nodes[o], color=edge_col, weight=edge_wgh)
                self.vis_dict['STMTS'].add_edge(edge)
                num_edges += 1
        # print 'DEBUG -- number of STMTS graph nodes:', \
        #  len(self.vis_dict['STMTS'].get_node_list())
        # print 'DEBUG -- number of TERMS graph edges:', \
        #  len(self.vis_dict['STMTS'].get_edge_list())

    def _gen_prov_vis(self, graph, max_nodes, max_edges, lex_labels=True):
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
            node_width = log(self.vis_par['BASE_WIDTH'] * puid2scale[puid], \
              self.vis_par['SCALE_BASE'])
            # enforcing a minimal size of the scaled nodes
            if node_width < 0.4:
                node_width = 0.4
            font_size = int(24 * node_width)  # 1/3 of the node, 72 points per inch
            # setting the node colour - distinguish between data and article
            # provenance by the fact that article provenance label is numeric,
            # while the data provenance is not
            node_col = self.vis_par['NCOL_MAP']['PROV_ART']
            if not node_name.split('_')[0].isdigit():
                node_col = self.vis_par['NCOL_MAP']['PROV_DAT']
            # print 'DEBUG -- provenance node name:', node_name
            # print 'DEBUG -- setting the provenance node colour to:', node_col
            # setting the node label either to the lexical name or to an ID
            label = node_label
            if lex_labels:
                label = node_name[:self.vis_par['MAX_NLABLEN']]
            # creating the node
            nodes[puid] = pydot.Node(\
              label, \
              style=self.vis_par['NODE_STYLE'], \
              fillcolor=node_col, \
              shape=self.vis_par['NODE_SHAPE'], \
              width=str(node_width), \
              fontsize=str(font_size), \
              fixedsize=self.vis_par['FIXED_SIZE']\
            )
            i += 1
        # adding the graph nodes to the PROVS visualisation
        for node in list(nodes.values()):
            self.vis_dict['PROVS'].add_node(node)
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
                #  str(prov_rels_set[(puid1,puid2)])[:self.vis_par['MAX_ELABLEN']]
                # edge = pydot.Edge(nodes[puid1],nodes[puid2],label=edge_label)
                edge_wgh = str(int(w * 10000))
                edge = pydot.Edge(nodes[puid1], nodes[puid2], weight=edge_wgh)
                self.vis_dict['PROVS'].add_edge(edge)
                num_edges += 1
        # print 'DEBUG -- number of PROVS graph nodes:', \
        #  len(self.vis_dict['PROVS'].get_node_list())
        # print 'DEBUG -- number of PROVS graph edges:', \
        #  len(self.vis_dict['PROVS'].get_edge_list())

    def node_info(self, graph_name, node_label):
        # provides additional information on a node in the visualisation graph

        if graph_name in ['TERMS', 'STMTS']:
            # checking for a term name corresponding to the queried label
            for label, name in self.vis_maps[graph_name]:
                if label == node_label:
                    return 'NODE METADATA:\n' + '  * NAME: ' + name
        elif graph_name == 'PROVS':
            # checking for a node with the requested label
            for label, name, _title in self.vis_maps[graph_name]:
                if label == node_label:
                    # generating a string from the provenance meta-data record
                    puid = name
                    # print 'DEBUG -- PUID:', puid
                    # print 'DEBUG -- name:', name
                    prov_meta = {}
                    if puid in self.index.puid2meta:
                        #prov_meta = self.index.puid2meta[puid]
                        prov_meta = 0.5
                    # print 'DEBUG -- meta:', prov_meta
                    lines = ['NODE METADATA:']
                    for key, value in list(prov_meta.items()):
                        lines.append('  * ' + str(key) + ': ' + str(value.encode('utf-8')))  # ,\
                        #  errors='replace')))
                    return '\n'.join(lines)
        return 'Node ' + node_label + ' not found in graph ' + graph_name + '...'

    def store(self, path):
        # storing all the result files to the specified path

        self._dump_term_xml(path)
        self._dump_stmt_xml(path)
        self._dump_prov_xml(path)
        # dumping the image graphs
        vis_path = os.path.join(path, self.vis_filenames['TERMS'])
        self.vis_dict['TERMS'].write_png(vis_path, prog=self.vis_par['PROG'])
        vis_path = os.path.join(path, self.vis_filenames['STMTS'])
        self.vis_dict['STMTS'].write_png(vis_path, prog=self.vis_par['PROG'])
        vis_path = os.path.join(path, self.vis_filenames['PROVS'])
        self.vis_dict['PROVS'].write_png(vis_path, prog=self.vis_par['PROG'])
        # dumping the raw graphs
        vis_path = os.path.join(path, self.vis_filenames['TERMS_RAW'])
        self.vis_dict['TERMS'].write(vis_path)
        vis_path = os.path.join(path, self.vis_filenames['STMTS_RAW'])
        self.vis_dict['STMTS'].write(vis_path)
        vis_path = os.path.join(path, self.vis_filenames['PROVS_RAW'])
        self.vis_dict['PROVS'].write(vis_path)
        # dumping the graph node name maps
        f = open(os.path.join(path, self.vis_filenames['TERMS_MAP']), 'w')
        f.write('\n'.join(['\t'.join(x) for x in self.vis_maps['TERMS']]))
        f.close()
        f = open(os.path.join(path, self.vis_filenames['STMTS_MAP']), 'w')
        f.write('\n'.join(['\t'.join(x) for x in self.vis_maps['STMTS']]))
        f.close()
        f = open(os.path.join(path, self.vis_filenames['PROVS_MAP']), 'w')
        f.write('\n'.join(['\t'.join(x) for x in self.vis_maps['PROVS']]))
        f.close()

    def _xml_elem(self, tag, attrib={}, text='', depth=0, children=[], indent_unit=2):
        # generates an XML element representation from the given tag, attrib
        # dictionary and text, with depth controlling the indentation

        hf_space = ' ' * (depth * indent_unit)  # header/footer space indent
        bd_space = ' ' * ((depth + 1) * indent_unit)  # body space indent
        attrib_strlist = []
        for key, value in list(attrib.items()):
            attrib_strlist.append(str(key) + '="' + str(value) + '"')
        lines = [hf_space + '<' + tag + ' ' + ' '.join(attrib_strlist) + '>']
        if len(text):
            lines += [bd_space + x for x in text.split('\n')]
        lines += children
        lines.append(hf_space + '</' + tag + '>')
        safe_lines = []
        for line in lines:
            try:
                safe_lines.append(line.encode('utf-8'))  # ,errors='replace'))
            except UnicodeDecodeError:
                sys.stderr.write('\nW @ _xml_elem(): problematic line, writing as:\n')
                sys.stderr.write(repr(line) + '\n')
                safe_lines.append(repr(line))
        return '\n'.join(safe_lines)

    def _dump_term_xml(self, path):
        # dumps the term XML

        f = open(os.path.join(path, self.term_filename), 'w')
        f.write('<?xml version="1.0" ?>\n<xml>\n')
        i = 0
        elements = []
        for tuid, w in self.tuid_cut.sort(reverse=True):
            i += 1
            # generating the child term element
            term_elem = self._xml_elem('term', text=tuid, depth=2)
            # the result element attributes
            attrib = {'rank':i, 'weight':w}
            res_elem = self._xml_elem('result', attrib=attrib, children=[term_elem], \
              depth=1)
            elements.append(res_elem)
        f.write('\n'.join(elements))
        f.write('\n</xml>')
        f.close()

    def _dump_stmt_xml(self, path):
        # dumps the term XML

        f = open(os.path.join(path, self.stmt_filename), 'w')
        f.write('<?xml version="1.0" ?>\n<xml>\n')
        i = 0
        elements = []
        for suid, w in self.suid_set.sort(reverse=True):
            i += 1
            # generating the child elements
            s, p, o, _corp_w = self.suid2stmt[suid]
            arg1_elem = self._xml_elem('argument', attrib={'pos':'L'}, \
              text=s, depth=2)
            rel_elem = self._xml_elem('relation', text=p, depth=2)
            arg2_elem = self._xml_elem('argument', attrib={'pos':'R'}, \
              text=o, depth=2)
            # the result element attributes
            attrib = {'rank':i, 'weight':w}
            children = [arg1_elem, rel_elem, arg2_elem]
            res_elem = self._xml_elem('result', attrib=attrib, children=children, \
              depth=1)
            elements.append(res_elem)
        f.write('\n'.join(elements))
        f.write('\n</xml>')
        f.close()

    def _dump_prov_xml(self, path):
        # dumps the term XML

        f = open(os.path.join(path, self.prov_filename), 'w')
        f.write('<?xml version="1.0" ?>\n<xml>\n')
        i = 0
        elements = []
        for puid, w in self.puid_set.sort(reverse=True):
            i += 1
            prov_meta = {}
            if puid in self.index.puid2meta:
                prov_meta = 0.5
                #prov_meta = self.index.puid2meta[puid]
            # generating the children elements
            children = []
            for key, value in list(prov_meta.items()):
                children.append(self._xml_elem(key, text=value, depth=2))
            # the result element attributes
            attrib = {'rank':i, 'weight':w}
            res_elem = self._xml_elem('result', attrib=attrib, children=children, \
              depth=1)
            elements.append(res_elem)
        f.write('\n'.join(elements))
        f.write('\n</xml>')
        f.close()

    def pretty_print(self, limit=10):
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