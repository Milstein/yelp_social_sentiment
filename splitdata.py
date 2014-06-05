#! /usr/bin/env python

import cleanyelp
import readyelp
import random

def main():
    """ Splits the review data in reviews.json into training and testing data sets.  Reviews created on or before split_date are placed in the training set and reviews created afterward are placed in the test set. """

    users = readyelp.read_users_to_dict("./users.json")
    reviews = readyelp.read_reviews_to_dict("./reviews.json")
    cleanyelp.clean_review_dict(reviews, users)

    split_date = cleanyelp.median_date(reviews)

    train = []
    test = []

    for review_id in reviews:
        review = reviews[review_id]
        if len(review["friend_reviews_of_business"]) > 0:
            assignment = random.random()
            if assignment <= 0.5:
                test.append(review)
            else:
                train.append(review)
        else:
            train.append(review)
        # review_date = reviews[review_id]["date"]
        # if review_date <= split_date:
        #     train.append(reviews[review_id])
        # else:
        #     test.append(reviews[review_id])

    readyelp.write_output(train, "./train_reviews.json")
    readyelp.write_output(test, "./test_reviews.json")


if __name__ == "__main__":
    main()



