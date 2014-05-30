#!/usr/bin/env/ python

import readyelp
import datetime

def _convert_review_date(date_string):
    """ Converts the string representation of a date to a python date object. """
    review_date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    return review_date


def _convert_star_rating_to_three_klass(star_rating):
    """ Converts the star attribute of a review to its corresponding sentiment value among positive, negative, and neutral. """
    if star_rating < 3:
        return "negative"
    elif star_rating > 3:
        return "positive"
    else:
        return "neutral"


def clean_review_dict(review_dict, user_dict):
    """ Removes reviews created by users not in user_dict, standardizes star ratings to their appropriate klass, standardizes review date to python date object. """
    ids_to_remove_from_reviews = []
    for review_id in review_dict:
        review = review_dict[review_id]
        review["rating"] = _convert_star_rating_to_three_klass(review["rating"])
        review_date_string = _convert_review_date(review["date"])
        if review["user_id"] not in user_dict:
            ids_to_remove_from_reviews.append(review_id)
        else:
            review_dict[review_id] = review
    for review_id in ids_to_remove_from_reviews:
        del review_dict[review_id]


def _user_reviews_by_business(review_ids, review_dict):
    """ Returns a dictionary mapping a business_id to a review_id. """
    review_dict_by_business = {}
    for r_id in review_ids:
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
        raw_counts[review["stars"]] += 1
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
        raw_counts[first_review["stars"]] += 1
        if first_review["stars"] == second_review["stars"]:
            homophily_counts[first_review["stars"]] += 1
    for klass in klass_list:
        print klass + " proportion of total, homophily proportion:", (raw_counts[klass]/total), (homophily_counts[klass] / raw_counts[klass])


def main():
    """ Invoking cleanyelp.py will output basic statistics from the yelp data. """
    user_dict = readyelp.read_users_to_dict("./users.json")
    print "Total number of users with friends:", len(user_dict)

    review_dict = readyelp.read_reviews_to_dict("./reviews.json")
    clean_review_dict(review_dict, user_dict)
    print "Total number of reviews from these users:", len(review_dict)

    common_review_pairs = find_review_pairs_by_friends(user_dict, review_dict)
    print "Total number of friend review pairs of the same business:", len(common_review_pairs)

    raw_counts = klass_counts(review_dict)
    for klass in klass_list:
        print "Total reviews with " + klass + " sentiment:", raw_counts[klass]
    _homophily_counts(common_review_pairs, review_dict)

if __name__ == "__main__":
    main()