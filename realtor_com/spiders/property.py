from datetime import datetime
from collections import OrderedDict

from .base import BaseSpider


class PropertySpider(BaseSpider):
    name = 'property'
    custom_settings = {
        'ITEM_PIPELINES': {
            'realtor_com.pipelines.PropertyscraperPipeline': 400,
        }
    }

    def parse_results(self, response):
        error_xpath = response.xpath("//div[contains(@class, 'not-found')]")
        if not error_xpath:
            for row in response.xpath("//div[contains(@data-label, 'property-card')]"):
                property_item = OrderedDict()

                # Get unique property id
                property_item['data_id'] = int(row.xpath("./@data-id").get())

                # Get property status
                row_property_status = row.xpath(".//div/div/div/@class").get()
                if 'statusLabelSection' in row_property_status:
                    property_item['status'] = row.xpath(".//div/div/div/span/text()").get()

                # Get property details
                row_property_details = row.xpath(".//div[contains(@class, 'property-wrap')]")
                if row_property_details:
                    property_item['price'] = row_property_details.xpath(".//div/span/text()").get()
                    property_item['beds'] = row_property_details.xpath(".//li[contains(@data-label, 'pc-meta-beds')]/span/text()").get()
                    property_item['baths'] = row_property_details.xpath(".//li[contains(@data-label, 'pc-meta-baths')]/span/text()").get()
                    property_item['sqft'] = row_property_details.xpath(".//li[contains(@data-label, 'pc-meta-sqft')]/span/text()").get()
                    property_item['sqftlot'] = row_property_details.xpath(".//li[contains(@data-label, 'pc-meta-sqftlot')]/span/text()").get()
                    property_item['address'] = row_property_details.xpath('.//div[contains(@data-label, "pc-address")]/text()').get()
                    property_item['city'] = ''
                    property_item['state'] = ''
                    property_item['zip_code'] = ''
                    row_address_second = row_property_details.xpath('.//div[contains(@data-label, "pc-address-second")]/text()')
                    if len(row_address_second) > 0:
                        try:
                            city, state, zip_code = '', '', ''
                            city = row_address_second[0].get().strip()
                            state = row_address_second[1].get().strip(', ')
                            zip_code = row_address_second[3].get().strip()
                            property_item['city'] = city
                            property_item['state'] = state
                            property_item['zip_code'] = zip_code
                        except IndexError:
                            pass

                # Get property link
                row_property_link = row.xpath(".//div/@class").get()
                if 'photo-wrap' in row_property_link:
                    property_item['url'] = row.xpath(".//div/a/@href").get()

                property_item['scraped_date_time'] = datetime.now()
                yield property_item

            # Check if next page is accessible
            next_page_element = response.xpath('//a[contains(@aria-label, "Go to next page")]')
            next_page = next_page_element.xpath('./@class').get()
            if 'disabled' not in next_page:
                next_page_url = next_page_element.xpath('./@href').get()
                if next_page_url:
                    yield response.follow(
                        url=next_page_url,
                        callback=self.parse_results,
                        headers=self.headers
                    )
