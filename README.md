# Real Estate Data Scraping
This project extracts real estate agents, companies and teams data from realtor.com using Scrapy. <br/>
Output is exported as a `csv` file.

## Setup Environment
* Install `poetry` https://python-poetry.org/docs/
* Install the dependencies by running the command `poetry install`

## Running Scripts
* City name and the 2-letter State abbreviation is required (use '-' if there are spaces in each word)
* Run the following command: <br/>
`sh scrape_agents.sh los-angeles ca`
