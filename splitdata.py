#! /usr/bin/env python

import cleanyelp
import readyelp
import random

SPLIT_RATIO = 0.9

def main():
    """ Splits the review data in reviews.json into training and testing data sets.  The proportion of the samples that are given to the training set is defined by the constant SPLIT_RATIO, above. """

    users = readyelp.read_users_to_dict("./users.json")
    reviews = readyelp.read_reviews_to_dict("./reviews.json")
    cleanyelp.clean_review_dict(reviews, users)

    train = []
    test = []

    for review_id in reviews:
        assignment = random.random()
        if assignment <= SPLIT_RATIO:
            train.append(reviews[review_id])
        else:
            test.append(reviews[review_id])

    readyelp.write_output(train, "./train_reviews.json")
    readyelp.write_output(test, "./test_reviews.json")


if __name__ == "__main__":
    main()



