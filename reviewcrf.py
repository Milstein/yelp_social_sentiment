#!/usr/bin/env python

import pycrfsuite
import readyelp
import random

def train_crf(train_reviews, user_dict):
    """ Given a dictionary of training reviews and a dictionary of user objects, trains a Linear-chain CRF model to tag pairs of reviews as either members of the same class (["1", "1"]) or different classes (["1", "0"]).  Features for the CRF consist of the date and text of each review. """
    trainer = pycrfsuite.Trainer('lbfgs')
    for train_id in train_reviews:
        train_review = train_reviews[train_id]
        friend_reviews_of_business = train_review["friend_reviews_of_business"]
        for friend_review_id in friend_reviews_of_business:
            if friend_review_id not in train_reviews: continue
            friend_review = train_reviews[friend_review_id]
            if friend_review["date"] <= train_review["date"]:
                train_user = user_dict[train_review["user_id"]]
                train_user_friend_set = set(train_user["friends"])
                friend_user = user_dict[friend_review["user_id"]]
                friend_user_friend_set = set(friend_user["friends"])
                mutual_friends = len(train_user_friend_set.intersection(friend_user_friend_set))
                friend_item = {"id":friend_review["review_id"], "date":friend_review["date"], "mutual_friends":mutual_friends}
                train_item = {"id":train_review["review_id"], "date":train_review["date"], "mutual_friends":mutual_friends}
                xseq = [friend_item, train_item]
                # If the ratings are the same between reviews, both are labeled as "1" in the Y sequence, otherwise the training review is labeled as "0".
                # This allows for the training of a CRF that determines the probability that the latter review receives the same label as the former - the strength of the link between reviews.
                if friend_review["rating"] == train_review["rating"]:
                    yseq = ["1", "1"]
                else:
                    yseq = ["1", "0"]

                trainer.append(xseq, yseq)
    trainer.train("reviewcrfmodel")

def crftag_probabilities(test_reviews, user_dict):
    """ Given a dictionary of reviews for test, tags pairs of reviews of the same business created by two users who are friends. Returns a dictionary mapping tuples (r1, r2) to the probability that those two reviews should receive the same classification. """
    probabilities = {}
    tagger = pycrfsuite.Tagger()
    tagger.open("reviewcrfmodel")
    for test_id in test_reviews:
        test_review = test_reviews[test_id]
        friend_reviews_of_business = test_review["friend_reviews_of_business"]
        for friend_review_id in friend_reviews_of_business:
            if friend_review_id not in test_reviews: continue
            friend_review = test_reviews[friend_review_id]
            if friend_review["date"] <= test_review["date"]:
                test_user = user_dict[test_review["user_id"]]
                test_user_friend_set = set(test_user["friends"])
                friend_user = user_dict[friend_review["user_id"]]
                friend_user_friend_set = set(friend_user["friends"])
                mutual_friends = len(test_user_friend_set.intersection(friend_user_friend_set))
                friend_item = {"id":friend_review["review_id"], "date":friend_review["date"], "mutual_friends":mutual_friends}
                test_item = {"id":test_review["review_id"], "date":test_review["date"], "mutual_friends":mutual_friends}
                xseq = [friend_item, test_item]
                yseq = tagger.tag(xseq)
                # The probability of the labeling yseq, given the input xseq
                prob_y = tagger.probability(yseq)
                probabilities[(friend_review_id, test_id)] = random.random()
                # if yseq[1] == "1":
                #     probabilities[(friend_review_id, test_id)] = prob_y
                # else:
                #     probabilities[(friend_review_id, test_id)] = 1 - prob_y
    return probabilities


def main():
    train_reviews = readyelp.read_reviews_to_dict("train_reviews.json")
    test_reviews = readyelp.read_reviews_to_dict("test_reviews.json")
    user_dict = readyelp.read_users_to_dict("users_limited.json")
    train_crf(train_reviews, user_dict)
    crftag(test_reviews, user_dict)

if __name__ == "__main__":
    main()