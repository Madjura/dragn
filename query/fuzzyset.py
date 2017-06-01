import sys
from _decimal import Decimal


class FuzzySet:
    """
    A simplistic (but efficient) implementation of a fuzzy set class and the
    basic operations (union, intersection, subtraction and complement) according
    to the standard definitions.
    """

    def __init__(self, elements=None):
        # initialising set, possibly with the (member,degree) pairs from elements

        if elements is None:
            elements = []
        self.members = {}
        for member, degree in elements:
            try:
                if 0 < degree <= 1:
                    self.members[member] = float(degree)
            except ValueError:
                sys.stderr.write('\nW @ FuzzySet(): invalid membership degree: ' +
                                 str(degree) + ' for the member: ' + str(member) + '\n')

    def __repr__(self):
        return str(list(self.members.items()))

    def __len__(self):
        return len(self.members)

    def __iter__(self):
        # iterator over the members (keys) to simulate a dictionary

        for member in list(self.members.keys()):
            yield member

    def __getitem__(self, member):
        # getting a membership degree of the member (zero if not present)

        if member in self.members:
            return self.members[member]
        else:
            return 0.0

    def __setitem__(self, member, degree):
        # setting a new degree for a member, possibly deleting it if the degree is
        # zero

        try:
            if degree == 0:
                if member in self.members:
                    del self.members[member]
            else:
                if degree <= 1:
                    self.members[member] = float(degree)
        except ValueError:
            sys.stderr.write('\nW @ FuzzySet(): invalid membership degree: ' +
                             str(degree) + ' for the member: ' + str(member) + '\n')

    def items(self):
        # all (member,degree) tuples via an iterator

        # for member, degree in self.members.items():
        #  yield (member,degree)
        return list(self.members.items())

    def keys(self):
        # all members

        # for member in self.members.keys():
        #  yield member
        return list(self.members.keys())

    def values(self):
        # all degrees

        # for degree in self.members.values():
        #  yield degree
        return list(self.members.values())

    def sort(self, reverse=False, limit=0):
        # iterator over items sorted from the least to most relevant (or reverse)

        l = [(x, d) for x, d in list(self.members.items())]
        l.sort(key=lambda x: x[1], reverse=reverse)
        i = 0
        for member, degree in l:
            yield member, degree
            i += 1
            if 0 < limit <= i:
                # if there is a limit and it was reached, stop
                break

    def update(self, elements, overwrite=True):
        # update the set values according to (member,degree) pairs in the elements,
        # overwriting possibly present elements by default

        for member, degree in elements:
            try:
                if overwrite:
                    self.members[member] = float(degree)
                else:
                    if not member in self.members:
                        self.members[member] = float(degree)
            except ValueError:
                sys.stderr.write('\nW @ FuzzySet(): invalid membership degree: ' +
                                 str(degree) + ' for the member: ' + str(member) + '\n')

    def cut(self, alpha=1.0):
        # returns an alpha-cut crisp set with the specified alpha

        return set([member for member, degree in list(self.items()) if degree >= alpha])

    def complement(self, universe=set()):
        # standard fuzzy set complement w.r.t. a given universe set (empty by
        # default, limiting the universe to the members present in this set)

        result = FuzzySet()
        # present member complement values
        for member, degree in list(self.items()):
            result[member] = 1.0 - degree
        # missing members from the universe
        for member in set(universe) - set(self.members.keys()):
            result[member] = 1.0
        return result

    def __sub__(self, other):
        # standard fuzzy set subtraction

        result = FuzzySet()
        # setting the result to self first
        for member, degree in list(self.members.items()):
            result[member] = degree
        # processing the elements from the other one
        for member in list(other.members.keys()):
            d = min(result[member], 1.0 - other[member])
            if d > 0:
                result[member] = d
        return result

    def __and__(self, other):
        # standard fuzzy set intersection

        result = FuzzySet()
        # process only shared members, the others are zero by definition
        for member in set(self.members.keys()) & set(other.members.keys()):
            result[member] = min(self.__getitem__(member), other[member])
        return result

    def __or__(self, other):
        # standard fuzzy set union

        result = FuzzySet()
        # process all members
        for member in set(self.members.keys()) | set(other.members.keys()):
            result[member] = max(self.__getitem__(member), other[member])
        return result

    @staticmethod
    def from_dictionary(dictionary):
        """
        Generates a FuzzySet from a dictionary.
            
            Args:
                dictionary: A dictionary in which the values are numerical.
            Returns:
                A FuzzySet object with normalised weights based on the input
                dictionary.
        """

        membership = FuzzySet()
        normalisation = Decimal(max(dictionary.values()))
        if normalisation <= 0:
            normalisation = Decimal(1)
        for key, value in dictionary.items():
            normalised = Decimal(value) / normalisation
            if normalised > 1:
                normalised = 1
            elif normalised < 0:
                normalised = 0
            membership[key] = normalised
        return membership
