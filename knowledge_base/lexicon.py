from os.path import sys, os
import re
from _collections import defaultdict

class Lexicon:
    """
    Two-way dictionary mapping lexical expressions to unique integer identifiers.
    """

    def __init__(self,items=[]):
        self.lex2int = {}
        self.int2lex = {}
        self.freqdct = defaultdict(int) ### changed to defaultdict
        self.frequency = defaultdict(int) ###
        self.terms = [] ###
        self.current = 0
        if len(items):
            self.update(items)

    def normalise(self,expr):
        # string normalisation
        return expr.lower().strip().replace(' ','_')

    def load(self,filename,normalise=True):
        # update the lexicon using a specified filename
        if normalise:
            self.update([self.normalise(x) for x in open(filename,'r')])
        else:
            self.update([x for x in open(filename,'r')])

    def from_file(self,filename):
        # import a lexicon from a tab-separated file (including the index mapping
        # and frequency of the token); expected format: token index frequency
        lines = []
        try:
            # assuming a file object
            tmp = str(filename.read())
            tmp = tmp.replace("\\t", "\t")
            tmp = tmp.split("\\n")
            lines = tmp
            #lines = filename.read().split('\n')
        except AttributeError:
            return
            # assuming a filename
            try:
                lines = open(filename,'r').read().split('\n')
            except:
                # if neither file nor filename, proceed with empty lines
                sys.stderr.write('W (importing a lexicon) - cannot import from: %s\n',\
                  str(filename))
        for line in lines:
            try:
                expr, indx, freq = line.split('\t')[:3]
                indx = int(indx)
                freq = int(freq)
                self.lex2int[expr] = indx
                self.int2lex[indx] = expr
                self.freqdct[expr] = freq
            except:
                sys.stderr.write('W (importing a lexicon) - fishy line:\n%s' % (line,))
        self.current = max(self.int2lex.keys()) + 1

    def to_file(self,filename):
        errors = 0
        # exporting a lexicon - inverse to import
        try:
            # assuming a file object
            #filename.write('\n'.join(['\t'.join([x,str(self.lex2int[x]),\
            #  str(self.freqdct[x])]) for x in self.lex2int]))
            for lex in self.lex2int:
                try:
                    tmp = ('\t'.join([lex, str(self.lex2int[lex]),
                                      str(self.freqdct[lex])
                                     ])+'\n')
                    filename.write(tmp.encode())
                except UnicodeEncodeError:
                    errors += 1
            filename.flush()
            os.fsync(filename.fileno())
        except AttributeError:
            # assuming a filename
            try:
                f = open(filename,'w')
                f.write('\n'.join(['\t'.join([x,str(self.lex2int[x]),\
                  str(self.freqdct[x])]) for x in self.lex2int]))
                f.close()
            except:
                # if neither file nor filename, proceed with empty lines
                sys.stderr.write('W (exporting a lexicon) - cannot export to: %s\n',\
                  str(filename))
        return errors

    def update_from_closeness(self, closenesses):
        """
        Updated update method. Not actively used, should accomplish what the 
        original tried to accomplish (and failed).
        """
        
        for closeness_list in closenesses:
            for closeness in closeness_list:
                self.frequency[closeness.term] += 1
                self.freqdct[closeness.term] += 1 ### experimental to keep his old stuff
                if closeness.term not in self.terms:
                    self.terms.append(closeness.term)

    def update(self, items: [str]):
        """
        Updates the lexicon with new terms.
        Terms are mapped to integers and vice versa.
        
            Args:
                items: A list of items to be inserted into the lexicon.
        """
        updates = []
        if type(items) is str:
            # make sure that single word updates are handled correctly
            updates = [items]
        else:
            # expect iterable here
            updates = list(items)
        for item in updates:
            # updating the frequency dictionary first
            if item in self.freqdct:
                self.freqdct[item] += 1
            else:
                self.freqdct[item] = 1
            if item not in self.lex2int:
                # udpate the dictionaries if the item is not present
                ## what the FUCK
                self.lex2int[item] = self.current
                self.int2lex[self.current] = item
                self.current += 1

    def __getitem__(self,key):
        if type(key) in [int,int]:
            if key in self.int2lex:
                return self.int2lex[key]
            else:
                raise KeyError('Index %s not present in the lexicon' % (key,))
        elif type(key) in [str,str]:
            if key in self.lex2int:
                print(self.lex2int[key])
                return self.lex2int[key]
            else:
                raise KeyError('Expression %s not present in the lexicon' % (key,))
        else:
            raise NotImplementedError('Unknown index or expression type: %s' % \
              (str(type(key)),))

    def has_key(self,key):
        if type(key) in [int,int]:
            return key in self.int2lex
        elif type(key) in [str,str]:
            return key in self.lex2int
        else:
            return False

    def __contains__(self,key):
        return key in self

    def items(self):
        return list(self.lex2int.items())

    def token_size(self):
        # size in overall number of non-unique tokens
        return sum(self.freqdct.values())

    def freq(self,token):
        # frequency of a token in the lexicon
        if type(token) in [str,str]:
            if token in self.freqdct:
                return self.freqdct[token]
            else:
                return 0
        elif type(token) in [int,int]:
            if self.int2lex[token] in self.freqdct:
                return self.freqdct[self.int2lex[token]]
            else:
                return 0
        else:
            return 0

    ### TODO: CHANGE THIS TO RETURN STRINGS INSTEAD OF INTS
    def sorted(self,reverse=True,limit=-1,ignored=[],lexical=False):
        # list of lexicalised tokens sorted according to their frequency;
        # limit can be one of the following:
        # < 0 ... no limit, all terms are returned
        # = 0 ... dynamic limit - all values with higher than average values, with
        #         the average computed while possibly omitting anything that
        #         matches any of the REs in ignored list
        # > 0 ... impose a limit
        l = list(self.freqdct.items())
        l.sort(key=lambda x: x[1],reverse=reverse)
        # restricting the list according to a possible limit value
        if limit > 0:
            # impose a fixed limit
            l = l[:limit]
        elif limit == 0:
            # compute a dynamic limit
            l_cut = []
            # creating a list without ignored stuff
            for item in l:
                ignore = False
                try:
                    for regexp in ignored:
                        if re.search(regexp,item[0]):
                            ignore = True
                            break
                except TypeError:
                    print("Error. Item was: ", item[0], " For regexp: ", regexp)
                if not ignore:
                    l_cut.append(item)
            # copmputing average from that list
            avg = sum([x[1] for x in l_cut])/float(len(l_cut)) ### average occurance, x[1] is the how ofen the phrase appears
            # including only the values >= average
            l = [x for x in l_cut if x[1] >= avg]
        else:
            # keep the list as is
            pass
        if lexical:
            # returning lexical values
            return [x[0] for x in l]
        # returning integer ID values
        return [x[0] for x in l] ### return not ids, but phrases/terms
        ###return [self.lex2int[x[0]] for x in l]
