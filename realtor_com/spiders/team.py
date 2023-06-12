from collections import OrderedDict

from .base import BaseSpider


class TeamSpider(BaseSpider):
    name = 'team'

    def parse_results(self, response):
        for row in response.xpath("//div[contains(@class, 'mobile-agent-card-wrapper')]/div/div"):
            row_class_title = row.xpath("./@class").get()
            if 'agent-list-card-title-text' in row_class_title:
                team_item = OrderedDict()
                team_item['name'] = row.xpath(".//a/div/text()").get()
                team_item['group'] = row.xpath(".//div[contains(@class, 'agent-group')]/span/text()").get()
                team_item['phone'] = row.xpath(".//div[contains(@class, 'agent-phone')]/text()").get()
                yield team_item
