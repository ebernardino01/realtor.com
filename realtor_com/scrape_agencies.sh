#!/bin/bash

export PATH=$PATH:/usr/local/bin:$HOME/.local/bin
DATE_WITH_TIME=`date "+%Y%m%dT%H%M%S"`
CITY_STATE="$1_$2"
poetry run scrapy runspider scrape_agencies.py -a city_state=${CITY_STATE} -O results/${CITY_STATE}_agency.csv --logfile logs/${CITY_STATE}-agencies-${DATE_WITH_TIME}.log
