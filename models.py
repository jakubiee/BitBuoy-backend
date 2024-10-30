from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class BuoyCreate(BaseModel):
    serial_number: str
    user_id: int
    
class MeasurementCreate(BaseModel):
    buoy_serial_number: str
    ambient_temp: float
    water_temp: float
    water_pollution: float
    humidity: float
    lat: float
    long: float
    timestamp: Optional[datetime] = None

class BuoyInfo(BaseModel):
    serial_number: str
    last_measurement_timestamp: Optional[datetime]
    lat: Optional[float]
    long: Optional[float]

class UserBuoysResponse(BaseModel):
    user_id: int
    buoys: List[BuoyInfo]

