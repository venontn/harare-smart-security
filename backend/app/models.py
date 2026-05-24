from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from .database import Base


class IncidentStatus(str, Enum):
    OPEN = "open"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class IncidentPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    zone = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    camera_type = Column(String(50), default="CCTV")
    status = Column(String(20), default="online")
    stream_url = Column(String(255), default="")


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    sensor_type = Column(String(50), nullable=False)
    zone = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default="active")
    last_value = Column(Float, default=0.0)
    unit = Column(String(20), default="")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    incident_type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    zone = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    priority = Column(String(20), default=IncidentPriority.MEDIUM.value)
    status = Column(String(20), default=IncidentStatus.OPEN.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    assigned_unit = Column(String(80), nullable=True)


class DispatchUnit(Base):
    __tablename__ = "dispatch_units"

    id = Column(Integer, primary_key=True, index=True)
    unit_name = Column(String(80), nullable=False)
    agency = Column(String(80), nullable=False)
    unit_type = Column(String(50), nullable=False)
    status = Column(String(20), default="available")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    current_incident_id = Column(Integer, nullable=True)


class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_name = Column(String(100), default="Anonymous")
    report_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    incident_id = Column(Integer, nullable=True)


class WatchlistPerson(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    national_id = Column(String(50), default="")
    reason = Column(String(200), nullable=False)
    risk_level = Column(String(20), default="medium")
    active = Column(Boolean, default=True)
    face_embedding = Column(Text, nullable=True)
    photo_file = Column(String(120), nullable=True)


class VehiclePlate(Base):
    __tablename__ = "vehicle_plates"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), nullable=False, unique=True, index=True)
    owner_name = Column(String(120), default="Unknown")
    vehicle_type = Column(String(50), default="private")
    status = Column(String(20), default="registered")  # registered, stolen, wanted
    notes = Column(String(200), default="")


class TrafficReading(Base):
    __tablename__ = "traffic_readings"

    id = Column(Integer, primary_key=True, index=True)
    intersection = Column(String(120), nullable=False)
    zone = Column(String(50), nullable=False)
    vehicle_count = Column(Integer, default=0)
    congestion_level = Column(String(20), default="low")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    zone = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium")
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    source_id = Column(Integer, nullable=True)
