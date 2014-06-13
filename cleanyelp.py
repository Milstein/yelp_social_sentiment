#!/usr/bin/env/ python

import readyelp
import datetime
import random


def split_data(train_ratio_of_total = 0.5):
    """ Splits the data randomly according to the ratio of training data to the total size of the data set provided.  The default argument of 0.5 splits the data evenly between training and test sets. """
    reviews = readyelp.read_reviews_to_dict("./reviews.json")
    users = readyelp.read_users_to_dict("./users.json")
    clean_review_dict(reviews, users)

    train = []
    test = []

    for review_id in reviews:
        review = reviews[review_id]
        assignment = random.random()
        if assignment <= train_ratio_of_total:
            train.append(review)
        else:
            test.append(review)

    readyelp.write_output(train, "./train_reviews.json")
    readyelp.write_output(test, "./test_reviews.json")
    filter_users()


def split_data_by_business(train_ratio_of_total = 0.5):
    """ Splits the data such that all reviews of a particular business end up in either the training set or the test set.  This prevents links between reviews from being lost during the split. """
    reviews = readyelp.read_reviews_to_dict("./reviews.json")
    users = readyelp.read_users_to_dict("./users.json")

    businesses = business_reviews_dict(reviews)

    train_ids = []
    test_ids = []

    for business_id in businesses:
        business_reviews = businesses[business_id]
        assignment = random.random()
        if assignment <= train_ratio_of_total:
            train_ids.extend(business_reviews)
        else:
            test_ids.extend(business_reviews)

    train = []
    test = []

    for train_id in train_ids:
        review = reviews[train_id]
        train.append(review)

    for test_id in test_ids:
        review = reviews[test_id]
        test.append(review)

    readyelp.write_output(train, "./train_reviews.json")
    readyelp.write_output(test, "./test_reviews.json")


def business_reviews_dict(reviews):
    businesses = {}

    for review_id in reviews:
        review = reviews[review_id]
        business_id = review["business_id"]
        if business_id in businesses:
            businesses[business_id].append(review_id)
        else:
            businesses[business_id] = [review_id]

    return businesses




def filter_users():
    """ Removes from the set of users any users that do not have reviews in either the training or test datasets. """
    user_dict = readyelp.read_users_to_dict("./users.json")
    train_reviews = readyelp.read_reviews_to_dict("./train_reviews.json")
    test_reviews = readyelp.read_reviews_to_dict("./test_reviews.json")

    users_limited = []

    for user_id in user_dict:
        user = user_dict[user_id]
        user_review_list = user["reviews"]
        for review_id in user_review_list:
            if review_id not in train_reviews and review_id not in test_reviews:
                user_review_list.remove(review_id)
        if len(user_review_list) > 0:
            user["reviews"] = user_review_list
            users_limited.append(user)

    readyelp.write_output(users_limited, "./users.json")


def find_influencers(review, review_dict, user_dict):
    """ Given a review, returns a list of reviews of the same business created by friends of the user who created the given review.  These reviews are thought to influence the sentiment of the given review. """
    influencers = []
    user = user_dict[review["user_id"]]
    friend_list = user["friends"]
    for friend_id in friend_list:
        friend = user_dict[friend_id]
        friend_review_list = friend["reviews"]
        for friend_review_id in friend_review_list:
            if friend_review_id not in review_dict: continue
            friend_review = review_dict[friend_review_id]
            if friend_review["business_id"] == review["business_id"]:
                influencers.append(friend_review_id)
    return influencers


def median_date(review_dict):
    review_dates = []
    for review_id in review_dict:
        review = review_dict[review_id]
        review_dates.append(review["date"])
    return review_dates[len(review_dates) / 2]


def _convert_review_date(date_string):
    """ Converts the string representation of a date to a python date object. """
    review_date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    return review_date


def _convert_star_rating_to_binary_klass(star_rating):
    """ Converts the star attribute of a review to its corresponding binary sentiment (negative or positive). """
    if star_rating <= 3:
        return "negative"
    else:
        return "positive"


def _convert_star_rating_to_three_klass(star_rating):
    """ Converts the star attribute of a review to its corresponding sentiment value among positive, negative, and neutral. """
    if star_rating < 3:
        return "negative"
    elif star_rating > 3:
        return "positive"
    else:
        return "neutral"


def clean_review_dict(review_dict, user_dict):
    """ Removes reviews created by users not in user_dict, standardizes star ratings to their appropriate klass, standardizes review date to python date object, and adds to each review a list of prior reviews of the same business by friends of the user. """
    ids_to_remove_from_reviews = []
    to_write_to_file = []
    for review_id in review_dict:
        review = review_dict[review_id]
        review["rating"] = _convert_star_rating_to_binary_klass(review["rating"])
        review_date_string = _convert_review_date(review["date"])
        if review["user_id"] not in user_dict:
            ids_to_remove_from_reviews.append(review_id)
        else:
            friend_reviews_of_business = find_influencers(review, review_dict, user_dict)
            if len(friend_reviews_of_business) == 0:
                ids_to_remove_from_reviews.append(review_id)
            else:
                review["friend_reviews_of_business"] = friend_reviews_of_business
                review_dict[review_id] = review
                to_write_to_file.append(review)
    for review_id in ids_to_remove_from_reviews:
        del review_dict[review_id]
    readyelp.write_output(to_write_to_file, "./reviews.json")


def _user_reviews_by_business(review_ids, review_dict):
    """ Returns a dictionary mapping a business_id to a review_id. """
    review_dict_by_business = {}
    for r_id in review_ids:
        if r_id not in review_dict: continue
        review = review_dict[r_id]
        review_dict_by_business[review["business_id"]] = r_id
    return review_dict_by_business


def find_review_pairs_by_friends(user_dict, review_dict):
    """ Returns a set of pairs of review_id's where a pair of friends reviewed the same business. """
    common_review_pairs = set()
    for user_id in user_dict:
        user = user_dict[user_id]
        user_friends = user["friends"]
        user_reviews = user["reviews"]
        user_businesses = _user_reviews_by_business(user_reviews, review_dict)
        for friend_id in user_friends:
            friend = user_dict[friend_id]
            friend_reviews = friend["reviews"]
            friend_businesses = _user_reviews_by_business(friend_reviews, review_dict)
            for business_id in friend_businesses:
                # Identify whether the friend reviewed any of the same businesses as the user and add review_id's to set.
                if business_id in user_businesses:
                    friend_review_id = friend_businesses[business_id]
                    friend_review = review_dict[friend_review_id]
                    user_review_id = user_businesses[business_id]
                    user_review = review_dict[user_review_id]
                    if user_review["date"] > friend_review["date"]:
                        common_review_pairs.add((user_review_id, friend_review_id))
                    elif user_review["date"] == friend_review["date"] and user_review_id > friend_review_id:
                        common_review_pairs.add((user_review_id, friend_review_id))
    return common_review_pairs


def klass_counts(review_dict, klass_list):
    counts = {"total" : 0}
    for klass in klass_list:
        counts[klass] = 0.0
    for review_id in review_dict:
        counts["total"] += 1
        review = review_dict[review_id]
        counts[review["rating"]] += 1
    return counts


def _homophily_counts(review_pairs, review_dict, klass_list):
    """ Counts instances of homophily in pairs of reviews, for each class.  Homophily is used here to mean that the later review shares the sentiment of the earlier review. """
    raw_counts = {}
    homophily_counts = {}
    total = 0
    for klass in klass_list:
        raw_counts[klass] = 0.0
        homophily_counts[klass] = 0.0
    for review_tuple in review_pairs:
        total += 1
        first_review = review_dict[review_tuple[0]]
        second_review = review_dict[review_tuple[1]]
        raw_counts[first_review["rating"]] += 1
        if first_review["rating"] == second_review["rating"]:
            homophily_counts[first_review["rating"]] += 1
    for klass in klass_list:
        print klass + " proportion of total, homophily proportion:", (raw_counts[klass]/total), (homophily_counts[klass] / raw_counts[klass])


def main():
    """ Invoking cleanyelp.py will output basic statistics from the yelp data. """
    user_dict = readyelp.read_users_to_dict("./users.json")
    print "Total number of users with friends:", len(user_dict)

    review_dict = readyelp.read_reviews_to_dict("./train_reviews.json")
    # clean_review_dict(review_dict, user_dict)
    print "Total number of reviews from these users:", len(review_dict)

    common_review_pairs = find_review_pairs_by_friends(user_dict, review_dict)
    print "Total number of friend review pairs of the same business:", len(common_review_pairs)


    klass_list = ["negative", "positive"]
    raw_counts = klass_counts(review_dict, klass_list)
    for klass in klass_list:
        print "Total reviews with " + klass + " sentiment:", raw_counts[klass]
    _homophily_counts(common_review_pairs, review_dict, klass_list)


if __name__ == "__main__":
    main()