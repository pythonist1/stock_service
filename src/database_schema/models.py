from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


# Таблица акций
class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)

    prices_and_trades = relationship("PriceAndTrade", back_populates="stock")
    company_info = relationship("StockCompanyInfo", uselist=False, back_populates="stock")


# Таблица цен и торгов
class PriceAndTrade(Base):
    __tablename__ = 'prices_and_trades'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id = Column(String, ForeignKey('stocks.id'))
    volume = Column(Float, nullable=False)  # Объем торгов
    opening_price = Column(Float, nullable=False)  # Цена открытия
    closing_price = Column(Float, nullable=False)  # Цена закрытия
    highest_price = Column(Float, nullable=False)  # Высокая цена
    lowest_price = Column(Float, nullable=False)  # Низкая цена
    number_of_trades = Column(Integer, nullable=False)  # Количество сделок
    timespan = Column(String, nullable=False)
    start_timestamp = Column(DateTime, nullable=False)  # Время
    timeinterval = Column(String, nullable=False, index=True)
    stock = relationship("Stock", back_populates="prices_and_trades")

    __table_args__ = (
        Index('ix_stocks_start_timestamp_timeinterval', 'start_timestamp', 'timeinterval'),
    )


# Таблица информации о компании и бирже
class StockCompanyInfo(Base):
    __tablename__ = 'stock_company_info'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id = Column(String, ForeignKey('stocks.id'))
    company_name = Column(String, nullable=False)
    market_type = Column(String, nullable=False)

    stock = relationship("Stock", back_populates="company_info")


def create_tables(engine):
    Base.metadata.create_all(engine)
