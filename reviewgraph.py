#!/usr/bin/env python

from graph_tool.all import *

def build_graph(klass_list, test_reviews, ind_pref, pair_str):
    """ Takes a dictionary of preferences for the individual document classifier (ind_pref) and a dictionary of strengths of links between pairs (pair_str).  For the former, keys are tuples of the form (r, c) where r is the review_id and c is the class assignment with highest probability.  The keys for the latter dictionary are tuples of the form (r1, r2) and values are the probability that r1 and r2 have the same class according to the Linear-chain CRF model.  Given these dictionaries, this method returns a graph object where each node is a review or a class.  Edges are defined by the keys to each of ind_pref and pair_str, and edge weight is the associated value. """
    g = Graph(directed = True)
    e_weight = g.new_edge_property("double")
    # Add nodes to the graph for each klass, "negative" and "positive"
    neg = g.add_vertex()
    pos = g.add_vertex()
    print "Added klass nodes."
    # Add a node to the graph for each review
    for test_review_id in test_reviews:
        test_review = test_reviews[test_review_id]
        v = g.add_vertex()
        test_review["vertex"] = v
        test_reviews[test_review_id] = test_review
    print "Added review nodes."
    # Add edges connecting each review to the class nodes where edge weight is determined by the individual classifier
    for review_id in ind_pref:
        review = test_reviews[review_id]
        e_neg = g.add_edge(neg, review["vertex"])
        e_pos = g.add_edge(review["vertex"], pos)
        e_weight[e_neg] = (1 - ind_pref[review_id])
        e_weight[e_pos] = (ind_pref[review_id])
    print "Added klass edges."
    # Add edges connecting pairs of reviews of the same business by friends
    for pair in pair_str:
        review_1 = test_reviews[pair[0]]
        review_2 = test_reviews[pair[1]]
        e = g.add_edge(review_1["vertex"], review_2["vertex"])
        e_weight[e] = pair_str[pair]
    print "Graph built."

    res = graph_tool.flow.push_relabel_max_flow(g, neg, pos, e_weight)
    print "Push Relabel run."
    min_cut, partition = graph_tool.flow.min_st_cut(g, neg, res)

    min_cut_classification = {}
    for review_id in test_reviews:
        review = test_reviews[review_id]
        vertex = review["vertex"]
        if partition[vertex]:
            min_cut_classification[review_id] = 0
        else:
            min_cut_classification[review_id] = 1


    return min_cut_classification


def mincutclassification(rgraph):
    """ Given a graph of reviews as defined above, returns a dictionary mapping review_id's to their classification according to the min cut (max flow) of the graph.  This min cut approach for classification is adapted from Bo Pang and Lillian Lee (2004). """
    max_flow = maximum_flow(rgraph, "negative", "positive")
    return max_flow[1]


def main():
    print "working"

if __name__ == "__main__":
    main()