import db
import os
from pprint import pprint

os.environ["DATABASE_URL"] = "postgres://amjtgvpjifijfn:ba7e78b1eb8f14ff893b7b59bc8a1ccd82268bc75f63c25c58b67add78d79405@ec2-54-217-245-26.eu-west-1.compute.amazonaws.com:5432/ddldso0ghvoc2m"

db = db.Db()

a = db.get_budget_detail("2018-11")

print("hi")

for x in a:
    print(x)

b = 3

