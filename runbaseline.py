#! /usr/bin/env python

""" Takes two arguments: the pathname for the Yelp Academic Dataset reviews json file and the users json file from the same dataset.  The dataset is available at https://www.yelp.com/dataset_challenge/dataset """

import readyelp
import cleanyelp
import splitdata
import baselineclassifier
import sys

review_path = sys.argv[1]
user_path = sys.argv[2]

reviews = []
users = []
reviews_by_user = {}
readyelp.parse_review_dataset_file(reviews, reviews_by_user, review_path)
readyelp.parse_user_dataset_file(users, reviews_by_user, user_path)
readyelp.write_output(reviews, "reviews.json")
readyelp.write_output(users, "users.json")

splitdata.main()

baselineclassifier.main()