import scrapy

from scrapy.utils.project import get_project_settings


class BaseSpider(scrapy.Spider):
    name = 'base'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results_by_page = get_project_settings().get('RESULTS_BY_PAGE')
        self.base_url = 'https://www.realtor.com'

    # Use an initial website to start scrapy request
    def start_requests(self):
        url = self.search_url
        yield scrapy.Request(url=url, callback=self.parse_count)

    # Get results count to determine page count
    def parse_count(self, response):
        results_xpath = response.xpath("//span[contains(@class, 'jsx-2957100293')]/span/text()")
        if not results_xpath:
            results_xpath = response.xpath("//span[contains(@class, 'jsx-2957100293')]/text()")

        results_label = results_xpath[1].get()
        results_count = results_label.split(' ')[0].replace(',', '')

        # Round the result to the nearest whole number
        page_count = int(-(-(int(results_count)) // self.results_by_page))
        for page in range(1, page_count + 1):
            page_url = f'{self.search_url}/pg-{page}'
            yield scrapy.Request(url=page_url, callback=self.parse_results)
