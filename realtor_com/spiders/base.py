from scrapy import Spider, Request

from scrapy.utils.project import get_project_settings


class BaseSpider(Spider):
    name = 'base'
    headers = {
        "Accept": get_project_settings().get('REQ_HEADERS_ACCEPT'),
        "Accept-Language": get_project_settings().get('REQ_HEADERS_ACCEPT_LANGUAGE'),
        "Accept-Encoding":  get_project_settings().get('REQ_HEADERS_ACCEPT_ENCODING'),
        "Cache-Control": get_project_settings().get('REQ_HEADERS_CACHE_CONTROL'),
        "Connection": get_project_settings().get('REQ_HEADERS_CONNECTION'),
        "Sec-Fetch-Dest": get_project_settings().get('REQ_HEADERS_SEC_FETCH_DEST'),
        "Sec-Fetch-Mode": get_project_settings().get('REQ_HEADERS_SEC_FETCH_MODE'),
        "Sec-Fetch-Site": get_project_settings().get('REQ_HEADERS_SEC_FETCH_SITE'),
        "Sec-Fetch-User": get_project_settings().get('REQ_HEADERS_SEC_FETCH_USER'),
        "Upgrade-Insecure-Requests": get_project_settings().get(
            'REQ_HEADERS_UPGRADE_INSECURE_REQUESTS'
        ),
        "User-Agent": get_project_settings().get('USER_AGENT'),
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = 'https://www.realtor.com'


    # Use an initial website to start scrapy request
    def start_requests(self):
        yield Request(
            url=self.search_url,
            callback=self.parse_results,
            headers=self.headers
        )


class RealtorSpider(BaseSpider):
    name = 'realtor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results_by_page = get_project_settings().get('REALTOR_RESULTS_BY_PAGE')
    

     # Use an initial website to start scrapy request
    def start_requests(self):
        yield Request(
            url=self.search_url,
            callback=self.parse_count,
            headers=self.headers
        )


    def parse_count(self, response):
        results_xpath = response.xpath("//span[contains(@class, 'jsx-2957100293')]/span/text()")
        if not results_xpath:
            results_xpath = response.xpath("//span[contains(@class, 'jsx-2957100293')]/text()")

        # Get results count to determine page count
        results_label = results_xpath[1].get()
        results_count = results_label.split(' ')[0].replace(',', '')

        # Round the result to the nearest whole number
        page_count = int(-(-(int(results_count)) // self.results_by_page))

        # Loop through each page
        for page in range(1, page_count + 1):
            page_url = f'{self.search_url}/pg-{page}'
            yield Request(
                url=page_url,
                callback=self.parse_results,
                headers=self.headers
            )
