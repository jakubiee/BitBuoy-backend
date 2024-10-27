from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
Base = declarative_base()

DATABASE_URL = "postgresql://postgres:HpLbfJhAEKeABEqaHosHwjCXKdAZVCKX@autorack.proxy.rlwy.net:51295/railway" 

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    buoys = relationship("Buoy", back_populates="user")

class Buoy(Base):
    __tablename__ = 'buoy'
    id = Column(Integer, primary_key=True)
    serial_number = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="buoys")
    measurements = relationship("Measurement", back_populates="buoy")
    createAt = Column(DateTime, default=datetime.utcnow)

class Measurement(Base):
    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    buoy_serial_number = Column(String, ForeignKey('buoy.serial_number'))
    ambient_temp = Column(Float)
    water_temp = Column(Float)
    water_pollution = Column(Float)
    humidity = Column(Float)
    lat = Column(Float)
    long = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    buoy = relationship("Buoy", back_populates="measurements")



engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


