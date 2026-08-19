from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./pricepilot.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="analyst") # admin, manager, analyst

class DBProduct(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True) # product_id from Olist
    category = Column(String, index=True)
    weight_g = Column(Float)
    length_cm = Column(Float)
    height_cm = Column(Float)
    width_cm = Column(Float)
    freight_value = Column(Float)
    base_price = Column(Float) # The median historical price or default price
    recommended_price = Column(Float, nullable=True)
    
    sales = relationship("DBSalesRecord", back_populates="product", cascade="all, delete-orphan")
    competitors = relationship("DBCompetitorPrice", back_populates="product", cascade="all, delete-orphan")

class DBSalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"))
    price = Column(Float)
    units_sold = Column(Integer)
    date = Column(Date)
    revenue = Column(Float)

    product = relationship("DBProduct", back_populates="sales")

class DBCompetitorPrice(Base):
    __tablename__ = "competitor_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"))
    competitor_name = Column(String)
    price = Column(Float)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("DBProduct", back_populates="competitors")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
