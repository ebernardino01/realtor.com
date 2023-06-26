# Real Estate Data Scraping
This project extracts real estate properties, agents, companies and teams data from realtor.com using Scrapy. <br/>
Agents, companies, and teams scraped output are exported as a `csv` file. <br/>
Properties scraped output are saved to `PostgreSQL` backend.

## Setup Environment
* Setup `postgresql` (database, user and grants needed)
* Install `poetry` https://python-poetry.org/docs/
* Setup environment variables in `.env`
* Install the dependencies by running the command `poetry install`

## Running Scripts
* City name and the 2-letter State abbreviation is required (use '-' if there are spaces in each word)
* Run the following command: <br/>
`sh scrape_agents.sh los-angeles ca` <br/>
OR: <br/>
`sh scrape_properties.sh los-angeles ca`
