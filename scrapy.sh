#!/bin/bash

url=$1
output=$2

# Run the Scrapy spider using the runspider command
scrapy runspider uniqlo_scraper.py -a url=$url -a out=$output