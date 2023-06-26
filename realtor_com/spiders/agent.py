from collections import OrderedDict

from .base import RealtorSpider


class AgentSpider(RealtorSpider):
    name = 'agent'

    def parse_results(self, response):
        for row in response.xpath("//div[contains(@class, 'mobile-agent-card-wrapper')]/div/div"):
            row_class_title = row.xpath("./@class").get()
            if 'agent-list-card-title-text' in row_class_title:
                agent_item = OrderedDict()
                agent_item['name'] = row.xpath(".//a/div/text()").get()
                agent_item['group'] = row.xpath(".//div[contains(@class, 'agent-group')]/span/text()").get()
                agent_item['phone'] = row.xpath(".//div[contains(@class, 'agent-phone')]/text()").get()
                yield agent_item
