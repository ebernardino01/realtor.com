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
                property_item['data_id'] = None
                property_id_text = row.xpath("./@id").get()
                property_id_text_list = property_id_text.split('_')
                if len(property_id_text_list) == 3:
                    property_item['data_id'] = int(property_id_text_list[2])

                # Get property media
                property_item['url'] = ''
                property_item['media_img'] = ''
                row_property_media = row.xpath(".//div[contains(@class, 'card-image-wrapper')]")
                if row_property_media:
                    # Property link
                    property_item['url'] = row_property_media.xpath(".//a/@href").get()

                    # Property image
                    property_item['media_img'] = row_property_media.xpath(".//a/div/picture/img/@src").get()

                # Get property details
                property_item['status'] = ''
                property_item['price'] = ''
                property_item['beds'] = ''
                property_item['baths'] = ''
                property_item['sqft'] = 0
                property_item['sqftlot'] = 0
                property_item['address'] = ''
                property_item['city'] = ''
                property_item['state'] = ''
                property_item['zip_code'] = ''
                row_property_details = row.xpath(".//div[contains(@class, 'card-content')]")
                if row_property_details:
                    # Property status
                    property_item['status'] = row_property_details.xpath(".//div[contains(@data-testid, 'card-description')]/div/text()").get()

                    # Property price
                    property_item['price'] = row_property_details.xpath(".//div[contains(@class, 'price-wrapper')]/div/text()").get()

                    # Property specifications
                    property_item['beds'] = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-beds')]/span/text()").get()
                    property_item['baths'] = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-baths')]/span/text()").get()

                    # Property area
                    row_area = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-sqft')]/span")
                    area = row_area.xpath(".//text()").get()
                    if area:
                        property_item['sqft'] = float(area.replace(',', ''))

                    # Property lot area
                    row_lot_area = row_property_details.xpath(".//li[contains(@data-testid, 'property-meta-lot-size')]/span")
                    area_lot = row_lot_area.xpath(".//text()").get()
                    area_lot_unit = row_lot_area.xpath("./text()").get()
                    if area_lot:
                        property_item['sqftlot'] = float(area_lot.replace(',', ''))
                        if area_lot_unit and 'acre' in area_lot_unit:
                            property_item['sqftlot'] = property_item['sqftlot'] * 43560

                    # Property address details
                    property_item['address'] = row_property_details.xpath('.//div[contains(@data-testid, "card-address-1")]/text()').get()
                    row_address_second_text = row_property_details.xpath('.//div[contains(@data-testid, "card-address-2")]/text()').get()
                    row_address_second = row_address_second_text.split(', ') if row_address_second_text else []
                    if len(row_address_second) > 0:
                        try:
                            property_item['city'] = row_address_second[0].strip()
                            row_state_zip = row_address_second[1].split(' ') if row_address_second[1] else []
                            property_item['state'] = row_state_zip[0].strip()
                            property_item['zip_code'] = row_state_zip[1].strip()
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
