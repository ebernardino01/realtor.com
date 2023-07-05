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
        # Check if error page is shown
        error_xpath = response.xpath("//div[contains(@class, 'error-404')]")
        if not error_xpath:
            for row in response.xpath("//div[contains(@class, 'BasePropertyCard_propertyCardWrap__J0xUj')]"):
                # Get unique property id
                property_item = OrderedDict()
                property_id_text = row.xpath("./@id").get()
                property_id_text_list = property_id_text.split('_')
                if len(property_id_text_list) == 3:
                    property_item['data_id'] = int(property_id_text_list[2])

                # Get property media
                row_property_media = row.xpath(".//div[contains(@class, 'card-image-wrapper')]")
                if row_property_media:
                    # Property link
                    property_item['url'] = row_property_media.xpath(".//a/@href").get()

                    # Property image
                    property_item['media_img'] = row_property_media.xpath(".//a/div/picture/img/@src").get()

                # Get property details
                row_property_details = row.xpath(".//div[contains(@class, 'card-content')]")
                if row_property_details:
                    # Property status
                    property_item['status'] = row_property_details.xpath(".//div[contains(@data-testid, 'card-description')]/div/text()").get()

                    # Property price
                    property_item['price'] = row_property_details.xpath(".//div[contains(@class, 'price-wrapper')]/div/text()").get()

                    # Property specifications
                    property_item['beds'] = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-beds')]/span/text()").get()
                    property_item['baths'] = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-baths')]/span/text()").get()
                    property_item['sqft'] = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-sqft')]/span/text()").get()
                    property_item['sqftlot'] = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-lot-size')]/span/text()").get()

                    # Property address details
                    property_item['address'] = row_property_details.xpath('.//div[contains(@data-testid, "card-address-1")]/text()').get()
                    property_item['city'] = ''
                    property_item['state'] = ''
                    property_item['zip_code'] = ''
                    row_address_second_text = row_property_details.xpath('.//div[contains(@data-testid, "card-address-2")]/text()').get()
                    row_address_second = row_address_second_text.split(' ') if row_address_second_text else []
                    if len(row_address_second) > 0:
                        try:
                            property_item['city'] = row_address_second[0].strip(', ')
                            property_item['state'] = row_address_second[1].strip()
                            property_item['zip_code'] = row_address_second[2].strip()
                        except IndexError:
                            pass

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
