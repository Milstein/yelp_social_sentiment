#!/usr/bin/env/ python

import json

def parse_review_dataset_file(reviews_output, reviews_by_user):
    """Reads yelp reviews from the specified json file from the Yelp Academic Dataset.  Adds relevant information (i.e., user_id, revew_id, business_id, stars, text, date) to output list and indexes reviews by user in reviews_by_user."""
    with open("../yelp_data/yelp_academic_dataset_review.json") as reviews_json_file:
        for line in reviews_json_file:
            review_in = json.loads(line)
            user_id  = review_in["user_id"]
            review_id = review_in["review_id"]
            review_out = {"user_id" : user_id, "review_id" : review_id, "business_id" : review_in["business_id"], "stars" : review_in["stars"], "text" : review_in["stars"], "date" : review_in["date"]}
            reviews_output.append(review_out)
            if user_id in reviews_by_user:
                reviews_by_user[user_id].append(review_id)
            else:
                reviews_by_user[user_id] = [review_id]
    reviews_json_file.closed


def parse_user_dataset_file(users_output, reviews_by_user):
    """Reads the yelp user json file and parses the user_id and list of friends for inclusion in the output file.  Users with no friends or no reviews in the dataset are excluded.  Includes list of reviews for each user in output list as in reviews_by_user."""
    with open("../yelp_data/yelp_academic_dataset_user.json") as users_json_file:
        for line in users_json_file:
            user_in = json.loads(line)
            user_id = user_in["user_id"]
            if user_in["friends"] and user_in["review_count"] is not 0:
                user_out = {"user_id" : user_id, "friends" : user_in["friends"], "reviews" : reviews_by_user[user_id]}
                users_output.append(user_out)
    users_json_file.closed


def write_output(object_list, output_path):
    """Given a list of json objects and a filepath, writes the objects to the file, one per line."""
    with open(output_path, 'w+') as output_file:
        for json_object in object_list:
            json.dump(json_object, output_file)
            output_file.write('\n')
    output_file.closed


def read_users_to_dict(input_path):
    """Returns a dictionary containing an object for each user in the file at input_path.  Keys are user_id's, values are objects as read from json input."""
    user_dict = {}
    with open(input_path) as input_file:
        for line in input_file:
            user_object = json.loads(line)
            user_dict[user_object["user_id"]] = user_object
    return user_dict


def read_reviews_to_dict(input_path):
    """Returns a dictionary of yelp reviews contained in the input file.  Keys are review_id, values are review objects read from json."""
    review_dict = {}
    with open(input_path) as input_file:
        for line in input_file:
            review_object = json.loads(line)
            review_dict[review_object["review_id"]] = review_object
    return review_dict



def main():
    users_output = []
    reviews_output = []
    reviews_by_user = {}

    # Populate reviews_output list and reviews_by_user dictionary from yelp json file
    parse_review_dataset_file(reviews_output, reviews_by_user)

    # Populate list of users for output
    parse_user_dataset_file(users_output, reviews_by_user)

    # Write output lists to new files
    write_output(users_output, "./users.json")
    write_output(reviews_output, "./reviews.json")



if __name__ == "__main__":
    main()
