# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging

from scrapy import Spider
from sqlalchemy.orm import sessionmaker

from realtor_com.models import Property, create_database_connection, create_tables

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class RealtorscraperPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        self.scraped_items = []
        try:
            engine = create_database_connection()
            create_tables(engine)
            self.Session = sessionmaker(bind=engine)
        except ValueError as ve:
            logger.exception(f"Database connection problem: {ve.args}")
            pass
        except Exception as e:
            logger.exception(f"Connection problem: {e.args}")
            pass

    def close_spider(self, spider: Spider) -> None:
        """
        Saving all the scraped events in bulk on spider close event
        """
        session = self.Session()
        try:
            logger.info("Saving events in bulk operation to the database...")
            session.add_all(self.scraped_items)
            session.commit()
        except Exception as e:
            logger.exception(e, extra=dict(spider=spider))
            session.rollback()
            raise
        finally:
            session.close()


class PropertyscraperPipeline(RealtorscraperPipeline):
    def process_item(self, item, spider: Spider):
        """
        This method is called for every item pipeline component
        """
        session = self.Session()

        # Check if scraped item already exists in the database
        existing_property = (
            session.query(Property)
            .filter_by(
                data_id=item["data_id"],
                address=item["address"],
                city=item["city"],
                state=item["state"],
                zip_code=item["zip_code"],
            )
            .first()
        )

        if not existing_property:
            property_item = Property()
            property_item.data_id = item["data_id"]
            property_item.url = item["url"]
            property_item.media_img = item["media_img"]
            property_item.status = item["status"]
            property_item.price = item["price"]
            property_item.beds = item["beds"]
            property_item.baths = item["baths"]
            property_item.sqft = item["sqft"]
            property_item.sqftlot = item["sqftlot"]
            property_item.address = item["address"]
            property_item.city = item["city"]
            property_item.state = item["state"]
            property_item.zip_code = item["zip_code"]
            property_item.scraped_date_time = item["scraped_date_time"]

            # Check first if the list already contains the item
            def is_duplicate(existing_item):
                return (
                    existing_item.data_id == property_item.data_id
                    and existing_item.url == property_item.url
                    and existing_item.address == property_item.address
                    and existing_item.city == property_item.city
                    and existing_item.state == property_item.state
                )

            if not any(filter(is_duplicate, self.scraped_items)):
                self.scraped_items.append(property_item)

        return item
