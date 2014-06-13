#! /usr/bin/env python

import readyelp
import cleanyelp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
import numpy
import random

def random_class():
    assignment = random.random()
    if assignment <= 0.5:
        return "positive"
    else:
        return "negative"

def influence_baseline(train_reviews, test_reviews, user_dict):
    """ Implements a baseline classifier that uses only review influencers.  That is, for each review in the test set, the label assigned is the majority label from the influencers of that review in the test set where an influencer is defined as a review of the same business at an earlier date from a user who is friends with the user who created the given test review. """
    Y_predict = []
    total_train_influencers = 0
    total_test_influences = 0
    no_influencers = 0
    for review_id in test_reviews:
        review = test_reviews[review_id]
        influencer_list = review["friend_reviews_of_business"]
        influence_sum = 0
        for influencer_id in influencer_list:
            if influencer_id in test_reviews:
                influencer = test_reviews[influencer_id]
            else:
                continue
            if influencer["rating"] == "negative":
                influence_sum -= 1
            else:
                influence_sum += 1
        if influence_sum < 0:
            Y_predict.append("negative")
        elif influence_sum > 0:
            Y_predict.append("positive")
        else:
            Y_predict.append("UNKNOWN")
    print "Total influencers in training set:", total_train_influencers
    print "Total influencers in test set:", total_test_influences
    print "Test reviews with no influencers:", no_influencers
    return Y_predict

def bag_of_words_probabilities(train_reviews, test_reviews):
    """ Implements a baseline bag-of-words classifier.  Returns a dictionary mapping tuples (review_id, class) to the probability that that review belongs to that class. """
    train_corpus = []
    test_corpus = []
    Y_train = []
    for review_id in train_reviews:
        review = train_reviews[review_id]
        train_corpus.append(review["text"])
        Y_train.append(review["rating"])

    vectorizer = CountVectorizer(stop_words = 'english')
    X_train = vectorizer.fit_transform(train_corpus)

    for review_id in test_reviews:
        review = test_reviews[review_id]
        test_corpus.append(review["text"])

    # clf = LinearSVC(class_weight = 'auto').fit(X_train, Y_train)
    # clf = LogisticRegression().fit(X_train, Y_train)
    clf = MultinomialNB().fit(X_train, Y_train)

    X_test = vectorizer.transform(test_corpus)
    Y_probability = clf.predict_proba(X_test)

    probability_dict = {}
    review_id_list = test_reviews.keys()
    for i in range(len(review_id_list)):
        probability_dict[review_id_list[i]] = Y_probability[i][1]

    return probability_dict


def bag_of_words_baseline(train_reviews, test_reviews):
    """ Runs the baseline classifier and returns an array of predicted classes. """
    Y_probability = bag_of_words_probabilities(train_reviews, test_reviews)
    Y_predict = []

    for review_id in test_reviews:
        p_pos = Y_probability[review_id]
        if p_pos < 0.5:
            Y_predict.append("negative")
        else:
            Y_predict.append("positive")

    return Y_predict



""" This module implements the baseline classifier.  MultinomialNB, LogisticRegression, and LinearSVC each give comparable performance in their current configurations. """
def main():
    train_reviews = readyelp.read_reviews_to_dict("./train_reviews.json")
    test_reviews = readyelp.read_reviews_to_dict("./test_reviews.json")
    user_dict = readyelp.read_users_to_dict("./users_limited.json")
    klass_list = ["negative", "positive"]
    test_corpus = []
    gold_labels = []
    Y_random = []
    for review_id in test_reviews:
        review = test_reviews[review_id]
        test_corpus.append(review["text"])
        gold_labels.append(review["rating"])
        Y_random.append(random_class())

    print "Random model metrics:"
    print metrics.classification_report(gold_labels, Y_random, target_names = klass_list)

    Y_bag_of_words = bag_of_words_baseline(train_reviews, test_reviews)
    print "Bag of words baseline model metrics:"
    print metrics.classification_report(gold_labels, Y_bag_of_words, target_names = klass_list)

    Y_random_influence = []
    Y_bow_influence = []
    Y_influence = influence_baseline(train_reviews, test_reviews, user_dict)
    for i in range(len(Y_influence)):
        if Y_influence[i] == "UNKNOWN":
            Y_bow_influence.append(Y_bag_of_words[i])
            Y_random_influence.append(Y_random[i])
        else:
            Y_bow_influence.append(Y_influence[i])
            Y_random_influence.append(Y_influence[i])

    print "Random influence baseline model metrics:"
    print metrics.classification_report(gold_labels, Y_random_influence, target_names = klass_list)

    print "Bag-of-words influence baseline model metrics:"
    print metrics.classification_report(gold_labels, Y_bow_influence, target_names = klass_list)




if __name__ == "__main__":
    main()