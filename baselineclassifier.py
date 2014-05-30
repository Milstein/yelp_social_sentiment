#! /usr/bin/env python

import readyelp
import cleanyelp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
import numpy

""" This module implements the baseline classifier.  MultinomialNB, LogisticRegression, and LinearSVC each give comparable performance in their current configurations. """
def main():
    train_reviews = readyelp.read_reviews_to_dict("./train_reviews.json")

    klass_list = ["negative", "neutral", "positive"]

    train_corpus = []
    Y_train = []
    for review_id in train_reviews:
        review = train_reviews[review_id]
        train_corpus.append(review["text"])
        Y_train.append(review["rating"])

    vectorizer = CountVectorizer(stop_words = 'english')
    X_train = vectorizer.fit_transform(train_corpus)

    # clf = LinearSVC(class_weight = 'auto').fit(X _train, Y_train)
    clf = LogisticRegression().fit(X_train, Y_train)
    # clf = MultinomialNB().fit(X, Y)

    test_reviews = readyelp.read_reviews_to_dict("./test_reviews.json")

    test_corpus = []
    gold_labels = []
    for review_id in test_reviews:
        review = test_reviews[review_id]
        test_corpus.append(review["text"])
        gold_labels.append(review["rating"])

    X_test = vectorizer.transform(test_corpus)
    Y_predict = clf.predict(X_test)

    print metrics.classification_report(gold_labels, Y_predict, target_names = klass_list)




if __name__ == "__main__":
    main()