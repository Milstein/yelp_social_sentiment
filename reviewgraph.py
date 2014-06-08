#!/usr/bin/env python

from pygraph.classes.digraph import digraph
from pygraph.algorithms.minmax import maximum_flow

def build_graph(klass_list, test_reviews, ind_pref, pair_str):
    """ Takes a dictionary of preferences for the individual document classifier (ind_pref) and a dictionary of strengths of links between pairs (pair_str).  For the former, keys are tuples of the form (r, c) where r is the review_id and c is the class assignment with highest probability.  The keys for the latter dictionary are tuples of the form (r1, r2) and values are the probability that r1 and r2 have the same class according to the Linear-chain CRF model.  Given these dictionaries, this method returns a graph object where each node is a review or a class.  Edges are defined by the keys to each of ind_pref and pair_str, and edge weight is the associated value. """
    rgraph = digraph()
    # Add nodes to the graph for each klass, "negative" and "positive"
    rgraph.add_nodes(klass_list)
    print "Added klass nodes."
    # Add a node to the graph for each review
    rgraph.add_nodes(test_reviews.keys())
    print "Added review nodes."
    # Add edges connecting each review to the class nodes where edge weight is determined by the individual classifier
    for edge in ind_pref:
        rgraph.add_edge(edge, ind_pref[edge])
    print "Added klass edges."
    # Add edges connecting pairs of reviews of the same business by friends
    for pair in pair_str:
        reverse_pair = (pair[1], pair[0])
        if not rgraph.has_edge(pair):
            rgraph.add_edge(pair, pair_str[pair])
        if not rgraph.has_edge(reverse_pair):
            rgraph.add_edge(reverse_pair, pair_str[pair])

    return rgraph


def mincutclassification(rgraph):
    """ Given a graph of reviews as defined above, returns a dictionary mapping review_id's to their classification according to the min cut (max flow) of the graph.  This min cut approach for classification is adapted from Bo Pang and Lillian Lee (2004). """
    max_flow = maximum_flow(rgraph, "negative", "positive")
    return max_flow[1]


def main():
    rgraph = digraph()

if __name__ == "__main__":
    main()