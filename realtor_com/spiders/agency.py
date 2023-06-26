from collections import OrderedDict

from .base import RealtorSpider


class AgencySpider(RealtorSpider):
    name = 'agency'

    def parse_results(self, response):
        for row in response.xpath("//div[contains(@class, 'mobile-agent-card-wrapper')]/div/div"):
            row_class_title = row.xpath("./@class").get()
            if 'agent-list-card-title-text' in row_class_title:
                agency_item = OrderedDict()
                agency_item['name'] = row.xpath(".//a/div[contains(@class, 'agent-name')]/text()").get()
                agency_item['group'] = row.xpath(".//div[contains(@class, 'agent-group')]/span/text()").get()
                agency_item['phone'] = row.xpath(".//div[contains(@class, 'agent-phone')]/text()").get()
                yield agency_item
