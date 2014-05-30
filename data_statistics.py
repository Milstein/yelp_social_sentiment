#!/usr/bin/env/ python

from parse_yelp_json import read_users_to_dict, read_reviews_to_dict
import datetime

klass_list = ["positive", "negative", "neutral"]

def convert_review_dates(review_dict):
    """Converts the string representation of a date to a python date object for each review."""
    for review_id in review_dict:
        review = review_dict[review_id]
        date_string = review["date"]
        review_date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        review["date"] = review_date
        review_dict[review_id] = review\


def convert_star_ratings_to_binary(review_dict):
    """Converts the star attribute of each review to 'negative' if the stars <= 3 and positiv if stars > 3."""
    for review_id in review_dict:
        review = review_dict[review_id]
        if review["stars"] < 3:
            review["stars"] = "negative"
        elif review["stars"] > 3:
            review["stars"] = "positive"
        else:
            review["stars"] = "neutral"
        review_dict[review_id] = review


def user_reviews_by_business(review_ids, review_dict):
    """Returns a dictionary mapping business_id's to reviews."""
    review_dict_by_business = {}
    for r_id in review_ids:
        review = review_dict[r_id]
        review_dict_by_business[review["business_id"]] = r_id
    return review_dict_by_business

def remove_reviews_from_users_without_friends(review_dict, user_dict):
    to_remove_from_reviews = []
    for review_id in review_dict:
        review = review_dict[review_id]
        if review["user_id"] not in user_dict:
            to_remove_from_reviews.append(review_id)
    for review_id in to_remove_from_reviews:
        del review_dict[review_id]

def find_review_pairs_by_friends(user_dict, review_dict):
    """Returns a set of pairs of review_id's where a pair of friends reviewed the same business."""
    friend_review_pairs = set()
    for user_id in user_dict:
        user = user_dict[user_id]
        user_friends = user["friends"]
        user_reviews = user["reviews"]
        user_businesses = user_reviews_by_business(user_reviews, review_dict)
        # Iterate through a user's friends
        for friend_id in user_friends:
            friend = user_dict[friend_id]
            friend_reviews = friend["reviews"]
            friend_businesses = user_reviews_by_business(friend_reviews, review_dict)
            # Iterate through the businesses reviewed by that friend
            for business_id in friend_businesses:
                # Identify whether the friend reviewed any of the same businesses as the user and add review_id's to set
                if business_id in user_businesses:
                    friend_review_id = friend_businesses[business_id]
                    friend_review = review_dict[friend_review_id]
                    user_review_id = user_businesses[business_id]
                    user_review = review_dict[user_review_id]
                    # First review in tuple is always earlier or on the same date as the second
                    if (user_review["date"] <= friend_review["date"]):
                        friend_review_pairs.add((user_review_id, friend_review_id))
    return friend_review_pairs

def klass_counts(review_pairs, review_dict):
    # Initialize both raw and homophily counts to 0 for each class
    raw_counts = {}
    homophily_counts = {}
    total = 0
    for klass in klass_list:
        raw_counts[klass] = 0.0
        homophily_counts[klass] = 0.0
    # Update counts from review pairs
    for review_tuple in review_pairs:
        total += 1
        first_review = review_dict[review_tuple[0]]
        second_review = review_dict[review_tuple[1]]
        raw_counts[first_review["stars"]] += 1
        if first_review["stars"] == second_review["stars"]:
            homophily_counts[first_review["stars"]] += 1
    # Print counts
    for klass in klass_list:
        print klass + " raw count and homophily: ", (raw_counts[klass]/total), (homophily_counts[klass] / raw_counts[klass])

def main():
    user_dict = read_users_to_dict("./users.json")
    print "Total number of users with friends is ", len(user_dict)

    review_dict = read_reviews_to_dict("./reviews.json")
    remove_reviews_from_users_without_friends(review_dict, user_dict)
    convert_review_dates(review_dict)
    convert_star_ratings_to_binary(review_dict)
    print "Total number of reviews from these users is ", len(review_dict)

    friend_review_pairs = find_review_pairs_by_friends(user_dict, review_dict)
    print "Total number of friend review pairs of the same business ", len(friend_review_pairs)

    klass_counts(friend_review_pairs, review_dict)

if __name__ == "__main__":
    main()