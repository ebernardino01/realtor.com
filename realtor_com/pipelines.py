# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from scrapy import Spider
from sqlalchemy.orm import sessionmaker

from realtor_com.models import Property, create_table, db_connect

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class RealtorscraperPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        try:
            engine = db_connect()
            create_table(engine)
            self.Session = sessionmaker(bind=engine)
            self.scraped_items = []
        except Exception as e:
            logger.error("Connection problem: ", e.args)
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
        except Exception as error:
            logger.exception(error, extra=dict(spider=spider))
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

        # Check if scraped item already exists
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
            self.scraped_items.append(property_item)

        return item
