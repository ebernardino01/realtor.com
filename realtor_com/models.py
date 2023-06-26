from dotenv import dotenv_values
from sqlalchemy import Column, create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import (
    BigInteger,
    DateTime,
    String
)


env = dotenv_values('.env')
DeclarativeBase = declarative_base()


def db_connect() -> Engine:
    """
    Creates database connection using database settings.
    Returns sqlalchemy engine instance
    """
    return create_engine(
        env.get('POSTGRES_URL'),
        pool_size=30,
        max_overflow=0
    )


def create_table(engine: Engine):
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
    price = Column("price", String)
    beds = Column("beds", String)
    baths = Column("baths", String)
    sqft = Column("sqft", String)
    sqftlot = Column("sqftlot", String)
    address = Column("address", String)
    city = Column("city", String)
    state = Column("state", String)
    zip_code = Column("zip_code", String)
    url = Column("url", String)
    scraped_date_time = Column('scraped_date_time', DateTime)