#!/usr/bin/env python

import readyelp
import cleanyelp
import baselineclassifier
import reviewcrf
import reviewgraph
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer

def main():

    ## Only call the below once, when data needs to be cleaned and split ##
    cleanyelp.split_data_by_business(0.75)
    #######################################################################

    train_reviews = readyelp.read_reviews_to_dict("./train_reviews.json")
    test_reviews = readyelp.read_reviews_to_dict("./test_reviews.json")
    user_dict = readyelp.read_users_to_dict("./users_limited.json")
    klass_list = ["negative", "positive"]

    # Calculate class preferences of individual classifier
    ind_pref = baselineclassifier.bag_of_words_probabilities(train_reviews, test_reviews)
    print "Individual preferences calculated."
    # Train CRF model
    reviewcrf.train_crf(train_reviews, user_dict)
    # Calculate pair strengths
    pair_str = reviewcrf.crftag_probabilities(test_reviews, user_dict)
    print "Pair strengths calculated."
    # Build review graph
    min_cut_classes = reviewgraph.build_graph(klass_list, test_reviews, ind_pref, pair_str)
    print "Graph cut."
    # Make min-cut classification
    Y_gold = []
    Y_predict = []
    for test_id in test_reviews:
        review = test_reviews[test_id]
        Y_gold.append(review["rating"])
        if min_cut_classes[test_id] == 1:
            Y_predict.append("positive")
        else:
            Y_predict.append("negative")

    classification_metrics = metrics.classification_report(Y_gold, Y_predict, target_names = klass_list)

    print classification_metrics


if __name__ == "__main__":
    main()