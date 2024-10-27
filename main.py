from fastapi import FastAPI, Depends, Header, HTTPException, Query
from database import SessionLocal, Buoy, Measurement
from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from models import BuoyCreate, MeasurementCreate, BuoyInfo, UserBuoysResponse, MeasurementData
from datetime import datetime


app = FastAPI()

API_TOKEN = "securetoken123"

def get_current_token(token: Optional[str] = Header(None)):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return token

@app.post("/buoy/")
def create_buoy(buoy: BuoyCreate, token: str = Depends(get_current_token)):
    session = SessionLocal()
    try:
        new_buoy = Buoy(serial_number=buoy.serial_number, user_id=buoy.user_id, createAt=datetime.now())
        session.add(new_buoy)
        session.commit()
        session.refresh(new_buoy)
        return {"message": "Buoy created successfully", "buoy_id": new_buoy.id}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Buoy already exists")
    finally:
        session.close()


@app.post("/measurement/")
def create_measurement(measurement: MeasurementCreate, token: str = Depends(get_current_token)):
    session = SessionLocal()
    try:
        buoy = session.query(Buoy).filter_by(serial_number=measurement.buoy_serial_number).first()
        if not buoy:
            raise HTTPException(status_code=404, detail="Buoy not found")

        new_measurement = Measurement(
            buoy_serial_number=measurement.buoy_serial_number,
            ambient_temp=measurement.ambient_temp,
            water_temp=measurement.water_temp,
            water_pollution=measurement.water_pollution,
            humidity=measurement.humidity,
            lat=measurement.lat,
            long=measurement.long,
            timestamp=measurement.timestamp or datetime.utcnow()
        )
        session.add(new_measurement)
        session.commit()
        session.refresh(new_measurement)
        return {"message": "Measurement added successfully", "measurement_id": new_measurement.id}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Failed to add measurement")
    finally:
        session.close()

@app.get("/user/{user_id}/buoys", response_model=UserBuoysResponse)
def get_user_buoys(user_id: int, token: str = Depends(get_current_token)):
    session = SessionLocal()
    try:
        buoys = session.query(Buoy).filter_by(user_id=user_id).all()
        if not buoys:
            raise HTTPException(status_code=404, detail="No buoys found for the user")

        buoys_info = []
        for buoy in buoys:
            last_measurement = (
                session.query(Measurement)
                .filter_by(buoy_serial_number=buoy.serial_number)
                .order_by(Measurement.timestamp.desc())
                .first()
            )
            last_timestamp = last_measurement.timestamp if last_measurement else None
            last_long = last_measurement.long if last_measurement else None
            last_lat = last_measurement.lat if last_measurement else None
            buoys_info.append(BuoyInfo(serial_number=buoy.serial_number, last_measurement_timestamp=last_timestamp, lat=last_lat, long=last_long))

        return UserBuoysResponse(user_id=user_id, buoys=buoys_info)
    finally:
        session.close()


@app.post("/measurements/", response_model=List[MeasurementData])
def get_measurements(
    serial_numbers: List[str] = Query(..., description="List of buoy serial numbers"),
    start_date: datetime = Query(..., description="Start date for data range"),
    end_date: datetime = Query(..., description="End date for data range"),
    token: str = Depends(get_current_token)
):
    session = SessionLocal()
    try:
        measurements = session.query(Measurement).filter(
            Measurement.buoy_serial_number.in_(serial_numbers),
            Measurement.timestamp >= start_date,
            Measurement.timestamp <= end_date
        ).all()

        if not measurements:
            raise HTTPException(status_code=404, detail="No measurements found for the given criteria")

        result = [
            MeasurementData(
                buoy_serial_number=m.buoy_serial_number,
                ambient_temp=m.ambient_temp,
                water_temp=m.water_temp,
                water_pollution=m.water_pollution,
                humidity=m.humidity,
                lat=m.lat,
                long=m.long,
                timestamp=m.timestamp
            )
            for m in measurements
        ]

        return result
    finally:
        session.close()