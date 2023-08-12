import logging

from common import run_spider
from spiders.agent import AgentSpider

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class RealtorAgentSpider(AgentSpider):
    # Allow spider to receive city and state arguments (separated by '_')
    def __init__(self, city_state=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_url = f"{self.base_url}/realestateagents/{city_state}"
        self.start_urls = [self.search_url]


if __name__ == "__main__":
    run_spider(RealtorAgentSpider)
