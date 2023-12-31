import logging
from collections import OrderedDict
from datetime import datetime
from http import HTTPStatus

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError

from .base import BaseSpider, request_headers

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class PropertySpider(BaseSpider):
    name = "property"
    custom_settings = {
        "ITEM_PIPELINES": {
            "realtor_com.pipelines.PropertyscraperPipeline": 400,
        }
    }

    def parse_results(self, response):
        """
        Callback to process the results of the request

        :param response: scrapy.http.HtmlResponse instance
        """
        # Check if error page is shown
        error_xpath = response.xpath("//div[contains(@class, 'error-404')]")
        if not error_xpath:
            # Check how many pages are present
            last_page_element = response.xpath(
                '//a[contains(@aria-label, "Go to next page")]/preceding-sibling::a[1]/@href'
            ).get()
            page_urls = OrderedDict()
            last_page_element_list = (
                last_page_element.split("pg-") if last_page_element else []
            )
            if len(last_page_element_list) > 1:
                # Construct the list of URLs based from the last page number
                last_page = last_page_element_list[1]
                if int(last_page) != 1:
                    for page in range(2, int(last_page) + 1):
                        page_urls[page] = f"{last_page_element_list[0]}pg-{page}"

            # Loop through each property items
            for row in response.xpath(
                "//div[contains(@class, 'BasePropertyCard_propertyCardWrap__J0xUj')]"
            ):
                # Get unique property id
                property_item = OrderedDict()
                property_item["data_id"] = None
                property_id_text = row.xpath("./@id").get()
                if len(property_id_text_list := property_id_text.split("_")) == 3:
                    property_item["data_id"] = int(property_id_text_list[2])

                # Get property media
                property_item["url"] = ""
                property_item["media_img"] = ""
                if row_property_media := row.xpath(
                    ".//div[contains(@class, 'card-image-wrapper')]"
                ):
                    # Property link
                    property_item["url"] = row_property_media.xpath(".//a/@href").get()

                    # Property image
                    property_item["media_img"] = row_property_media.xpath(
                        ".//a/div/picture/img/@src"
                    ).get()

                # Get property details
                property_item["status"] = ""
                property_item["price"] = ""
                property_item["beds"] = ""
                property_item["baths"] = ""
                property_item["sqft"] = 0
                property_item["sqftlot"] = 0
                property_item["address"] = ""
                property_item["city"] = ""
                property_item["state"] = ""
                property_item["zip_code"] = ""
                if row_property_details := row.xpath(
                    ".//div[contains(@class, 'card-content')]"
                ):
                    # Property status
                    property_item["status"] = row_property_details.xpath(
                        ".//div[contains(@data-testid, 'card-description')]/div/text()"
                    ).get()

                    # Property price
                    property_item["price"] = row_property_details.xpath(
                        ".//div[contains(@class, 'price-wrapper')]/div/text()"
                    ).get()

                    # Property specifications
                    property_item["beds"] = row_property_details.xpath(
                        ".//li[contains(@data-testid, 'property-meta-beds')]/span/text()"
                    ).get()
                    property_item["baths"] = row_property_details.xpath(
                        ".//li[contains(@data-testid, 'property-meta-baths')]/span/text()"
                    ).get()

                    # Property area
                    row_area = row_property_details.xpath(
                        ".//li[contains(@data-testid, 'property-meta-sqft')]/span"
                    )
                    if area := row_area.xpath(".//text()").get():
                        property_item["sqft"] = float(area.replace(",", ""))

                    # Property lot area
                    row_lot_area = row_property_details.xpath(
                        ".//li[contains(@data-testid, 'property-meta-lot-size')]/span"
                    )
                    if area_lot := row_lot_area.xpath(".//text()").get():
                        property_item["sqftlot"] = float(area_lot.replace(",", ""))
                        area_lot_unit = row_lot_area.xpath("./text()").get()
                        if area_lot_unit and "acre" in area_lot_unit:
                            property_item["sqftlot"] = property_item["sqftlot"] * 43560

                    # Property address details
                    property_item["address"] = row_property_details.xpath(
                        './/div[contains(@data-testid, "card-address-1")]/text()'
                    ).get()
                    row_address_second_text = row_property_details.xpath(
                        './/div[contains(@data-testid, "card-address-2")]/text()'
                    ).get()
                    row_address_second = (
                        row_address_second_text.split(", ")
                        if row_address_second_text
                        else []
                    )
                    if len(row_address_second) > 0:
                        try:
                            property_item["city"] = row_address_second[0].strip()
                            row_state_zip = (
                                row_address_second[1].split(" ")
                                if row_address_second[1]
                                else []
                            )
                            property_item["state"] = row_state_zip[0].strip()
                            property_item["zip_code"] = row_state_zip[1].strip()
                        except IndexError:
                            pass

                property_item["scraped_date_time"] = datetime.now()
                yield property_item

            # Loop through the URL list for the succeeding pages
            for index in sorted(page_urls.keys()):
                yield response.follow(
                    url=page_urls[index],
                    callback=self.parse_results,
                    headers=request_headers,
                    errback=self.handle_error,
                )

    def handle_error(self, failure):
        """
        Error callback function

        :param failure: Twisted Failure instance
        """

        if failure.check(HttpError):
            # Check if the failure is due to a 403 error
            if failure.value.response.status == HTTPStatus.FORBIDDEN:
                logger.warning(
                    "Skipping URL due to 403 error: %s", failure.value.response.url
                )
            else:
                logger.error("Error processing URL: %s", failure.value.response.url)
        elif failure.check(DNSLookupError, TimeoutError, TCPTimedOutError):
            # Check also for DNS lookup and timeout errors
            logger.error(failure.getErrorMessage())
