#! /usr/bin/env python

import readyelp
import cleanyelp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
import numpy
import random


def influence_baseline(train_reviews, test_reviews, user_dict):
    """ Implements a baseline classifier that uses only review influencers.  That is, for each review in the test set, the label assigned is the majority label from the influencers of that review in the training set where an influencer is defined as a review of the same business at an earlier date from a user who is friends with the user who created the given test review. """
    Y_predict = []
    randomized_labels = 0
    non_random = 0
    for review_id in test_reviews:
        review = test_reviews[review_id]
        influencer_list = cleanyelp.find_influencers(review, train_reviews, user_dict)
        if len(influencer_list) == 0:
            Y_predict.append("UNKNOWN")
            continue
        else:
            non_random += 1
            influence_sum = 0
            for influencer_id in influencer_list:
                influencer = train_reviews[influencer_id]
                if influencer["rating"] == "negative":
                    influence_sum -= 1
                else:
                    influence_sum += 1
            if influence_sum < 0:
                Y_predict.append("negative")
            else:
                Y_predict.append("positive")
    return Y_predict

def bag_of_words_baseline(train_reviews, test_corpus):
    """ Implements a baseline bag-of-words classifier. """
    train_corpus = []
    Y_train = []
    for review_id in train_reviews:
        review = train_reviews[review_id]
        train_corpus.append(review["text"])
        Y_train.append(review["rating"])

    vectorizer = CountVectorizer(stop_words = 'english')
    X_train = vectorizer.fit_transform(train_corpus)

    # clf = SVC(class_weight = 'auto').fit(X_train, Y_train)
    # clf = LogisticRegression().fit(X_train, Y_train)
    clf = MultinomialNB().fit(X_train, Y_train)

    X_test = vectorizer.transform(test_corpus)
    Y_predict = clf.predict(X_test)

    return Y_predict

""" This module implements the baseline classifier.  MultinomialNB, LogisticRegression, and LinearSVC each give comparable performance in their current configurations. """
def main():
    train_reviews = readyelp.read_reviews_to_dict("./train_reviews.json")
    test_reviews = readyelp.read_reviews_to_dict("./test_reviews.json")
    user_dict = readyelp.read_users_to_dict("./users.json")
    klass_list = ["negative", "positive"]
    test_corpus = []
    gold_labels = []
    for review_id in test_reviews:
        review = test_reviews[review_id]
        test_corpus.append(review["text"])
        gold_labels.append(review["rating"])

    Y_bag_of_words = bag_of_words_baseline(train_reviews, test_corpus)
    print "Bag of words baseline model metrics:"
    print metrics.classification_report(gold_labels, Y_bag_of_words, target_names = klass_list)

    Y_influence = influence_baseline(train_reviews, test_reviews, user_dict)
    for i in range(len(Y_influence)):
        if Y_influence[i] == "UNKNOWN":
            Y_influence[i] = Y_bag_of_words[i]
    print "Influence baseline model metrics:"
    print metrics.classification_report(gold_labels, Y_influence, target_names = klass_list)




if __name__ == "__main__":
    main()