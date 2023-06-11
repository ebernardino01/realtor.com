#!/bin/bash

export PATH=$PATH:/usr/local/bin:$HOME/.local/bin
DATE_WITH_TIME=`date "+%Y%m%dT%H%M%S"`
CITY_STATE="$1_$2"
poetry run scrapy runspider scrape_agents.py -a city_state=${CITY_STATE} -O results/${CITY_STATE}_agent.csv --logfile logs/${CITY_STATE}-agents-${DATE_WITH_TIME}.log
