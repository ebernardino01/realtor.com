from dotenv import dotenv_values
from scrapy.utils.project import get_project_settings
from sqlalchemy import Column, create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Float, String

DeclarativeBase = declarative_base()


def create_database_connection() -> Engine:
    """
    Creates database connection using database settings.

    Returns sqlalchemy engine instance.
    """
    env = dotenv_values(".env")
    db_url = env.get(
        "POSTGRES_URL", get_project_settings().get("REALTOR_POSTGRES_URL_LOCAL")
    )
    if db_url is None:
        raise ValueError("Database connection URL cannot be None")
    return create_engine(
        db_url,
        pool_size=30,
        max_overflow=0,
    )


def create_tables(engine: Engine):
    """
    Create all tables stored in this metadata.
    Conditional by default, will not attempt to recreate tables already present in the target database.

    :param engine: connectable to access the database
    """
    DeclarativeBase.metadata.create_all(engine)


class Property(DeclarativeBase):
    """
    Defines the property model
    """

    __tablename__ = "property"

    id = Column("id", BigInteger, primary_key=True)
    data_id = Column(BigInteger, index=True)
    url = Column("url", String)
    media_img = Column("media_img", String)
    status = Column("status", String)
    price = Column("price", String)
    beds = Column("beds", String)
    baths = Column("baths", String)
    sqft = Column("sqft", Float)
    sqftlot = Column("sqftlot", Float)
    address = Column("address", String)
    city = Column("city", String)
    state = Column("state", String)
    zip_code = Column("zip_code", String)
    scraped_date_time = Column("scraped_date_time", DateTime)
