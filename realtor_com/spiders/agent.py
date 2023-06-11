import scrapy

from collections import OrderedDict


class AgentSpider(scrapy.Spider):
    name = 'agent'

    # Use an initial website to start scrapy request
    def start_requests(self):
        url = self.search_url
        yield scrapy.Request(url=url, callback=self.parse_count)

    # Get results count to determine page count
    def parse_count(self, response):
        results_label = response.xpath("//span[contains(@class, 'jsx-2957100293')]/span/text()")[1].get()
        results_count = results_label.split(' ')[0].replace(',', '')

        # Round the result to the nearest whole number
        page_count = int(-(-(int(results_count)) // self.results_by_page))
        for page in range(1, page_count + 1):
            page_url = f'{self.search_url}/pg-{page}'
            yield scrapy.Request(url=page_url, callback=self.parse_results)


    def parse_results(self, response):
        for row in response.xpath("//div[contains(@class, 'mobile-agent-card-wrapper')]/div/div"):
            row_class_title = row.xpath("./@class").get()
            if 'agent-list-card-title-text' in row_class_title:
                agent_item = OrderedDict()
                agent_item['name'] = row.xpath(".//a/div/text()").get()
                agent_item['group'] = row.xpath(".//div[contains(@class, 'agent-group')]/span/text()").get()
                agent_item['phone'] = row.xpath(".//div[contains(@class, 'agent-phone')]/text()").get()
                yield agent_item
