#!/usr/bin/env python3
import pymongo
from bson.json_util import dumps
from bson import json_util
from datetime import datetime, timedelta
import sys

URI_STRING = "mongodb+srv://USERNAME:PASSWORD@ATLAS_CLUSTER.mongodb.net/test?retryWrites=true&w=majority"

def findWithGranularResitrction(query, user):
    # Define the MongoDB Connection
    conn=pymongo.MongoClient(URI_STRING)
    db = conn["access_control"]

    # Define the collections we will be working with
    events_collection = db["events"]
    perms_collection = db["user_perms"]

    # Retrieve the user permissions record for the given user
    user_perms = perms_collection.find_one({"userid": user})

    if user_perms == None:
        # Exit if no user permissions record was returned
        sys.exit("User '{}' does not have a permissions record".format(user))
    
    # Set the filter to the filter defined in the user permissions record else set to None
    filter = user_perms['filter'] if 'filter' in user_perms else None
    
    # Set the projection to the projection defined in the user permissions record else set to None
    projection = user_perms['projection'] if 'projection' in user_perms else None
    
    # Update the query object with the filter (i.e. add the filter parameters to the query object)
    query.update(filter)
    
    # Print the query and projection objects for inspection
    print()
    print("##########")
    print("Query Object")
    print(dumps(query, indent=2))
    print("##########")
    print()
    print("##########")
    print("Projection Object")
    print(dumps(projection, indent=2))
    print("##########")
    print()
    
    # Get results cursor
    results = events_collection.find(query, projection).limit(3)
    
    # Print each result in the cursor
    for result in results:
        print(dumps(result, indent=2))

# Set the user variable based on the argument provided on the command line
if len(sys.argv) >= 2:
    arg_user = sys.argv[1]
else:
    sys.exit("User not provided as argument on command line")

# Call the function defined above with a query targeting events in the last 24 hours
findWithGranularResitrction(
    {"eventDateTime": {"$gt": datetime(2020, 5, 10), "$lt": datetime(2020, 5, 11)}},
    arg_user
)