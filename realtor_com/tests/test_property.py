import unittest
from collections import OrderedDict
from unittest.mock import patch

from betamax import Betamax
from betamax.fixtures.unittest import BetamaxTestCase
from scrapy.http import HtmlResponse

from realtor_com.spiders.base import request_headers
from realtor_com.spiders.property import PropertySpider

# Configure Betamax
with Betamax.configure() as config:
    config.cassette_library_dir = "realtor_com/tests/cassettes"
    config.preserve_exact_body_bytes = True


class TestPropertySpider(BetamaxTestCase):
    def test_parse_results(self):
        # Create a Scrapy Request object with headers
        property_spider = PropertySpider()
        url = "https://www.realtor.com/realestateandhomes-search/tampa_fl"

        # Mock response.follow to prevent actual requests
        with patch("scrapy.http.HtmlResponse.follow") as mock_follow:
            mock_follow.return_value = []

            # Run the spider with the mocked response.follow
            with self.recorder.use_cassette("test_property_cassette"):
                response = self.session.get(url=url, headers=request_headers)

                # Create a Scrapy Response object from the request session
                scrapy_response = HtmlResponse(
                    url=response.url, body=response.content, encoding="utf-8"
                )

                # Run the parse method
                result = property_spider.parse_results(scrapy_response)

                # Check the parse result type of the first item returned
                filter_list = [item for item in list(result) if item != []]
                self.assertEqual(type(filter_list[0]), OrderedDict)

                # Check the parse result structure
                yield_keys = [
                    "data_id",
                    "url",
                    "media_img",
                    "status",
                    "price",
                    "beds",
                    "baths",
                    "sqft",
                    "sqftlot",
                    "address",
                    "city",
                    "state",
                    "zip_code",
                    "scraped_date_time",
                ]
                self.assertEqual(yield_keys, list(filter_list[0].keys()))
                self.assertEqual(len(yield_keys), len(list(filter_list[0].keys())))


if __name__ == "__main__":
    unittest.main()
