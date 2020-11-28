# Boba Scraper Overview
Simple python scraper that runs through each entry for all the pages of each nyc borough to count the total number of boba spots in that certain borough.  

# Data source
Yelp. 

# Error Checking 
The location aspect of the search returns "near [borough]" and there's two problems this introduces:
    1. repeated values (all boros are near each other).
    2. locations have to be verified (e.g. Manhattan search will include BK results).
Resepctive solutions:
    1. OOP solution: resturuant entry objects with '==' implemented. maintain global list to keep track of data we already saw (and counted).
    2. google maps geoencoding api to verify borough before counting it.