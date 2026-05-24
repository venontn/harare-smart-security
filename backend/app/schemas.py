from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CameraOut(BaseModel):
    id: int
    name: str
    zone: str
    latitude: float
    longitude: float
    camera_type: str
    status: str
    stream_url: str

    class Config:
        from_attributes = True


class SensorOut(BaseModel):
    id: int
    name: str
    sensor_type: str
    zone: str
    latitude: float
    longitude: float
    status: str
    last_value: float
    unit: str

    class Config:
        from_attributes = True


class IncidentCreate(BaseModel):
    title: str
    description: str = ""
    incident_type: str
    source: str
    zone: str
    latitude: float
    longitude: float
    priority: str = "medium"


class IncidentOut(BaseModel):
    id: int
    title: str
    description: str
    incident_type: str
    source: str
    zone: str
    latitude: float
    longitude: float
    priority: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]
    assigned_unit: Optional[str]

    class Config:
        from_attributes = True


class DispatchUnitOut(BaseModel):
    id: int
    unit_name: str
    agency: str
    unit_type: str
    status: str
    latitude: float
    longitude: float
    current_incident_id: Optional[int]

    class Config:
        from_attributes = True


class DispatchRequest(BaseModel):
    incident_id: int
    unit_id: int


class CitizenReportCreate(BaseModel):
    reporter_name: str = "Anonymous"
    report_type: str
    description: str
    latitude: float = Field(..., ge=-18.0, le=-17.5)
    longitude: float = Field(..., ge=30.8, le=31.2)


class CitizenReportOut(BaseModel):
    id: int
    reporter_name: str
    report_type: str
    description: str
    latitude: float
    longitude: float
    status: str
    created_at: datetime
    incident_id: Optional[int]

    class Config:
        from_attributes = True


class WatchlistOut(BaseModel):
    id: int
    full_name: str
    national_id: str
    reason: str
    risk_level: str
    active: bool
    has_face_enrolled: bool = False
    photo_file: Optional[str] = None

    class Config:
        from_attributes = True


class VehiclePlateOut(BaseModel):
    id: int
    plate_number: str
    owner_name: str
    vehicle_type: str
    status: str
    notes: str

    class Config:
        from_attributes = True


class TrafficOut(BaseModel):
    id: int
    intersection: str
    zone: str
    vehicle_count: int
    congestion_level: str
    latitude: float
    longitude: float
    recorded_at: datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    alert_type: str
    message: str
    zone: str
    severity: str
    acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    active_incidents: int
    open_alerts: int
    cameras_online: int
    sensors_active: int
    units_available: int
    citizen_reports_pending: int
    critical_incidents: int
    zones_monitored: int


class CrimeHotspot(BaseModel):
    zone: str
    incident_count: int
    dominant_type: str
    risk_score: float


class FaceMatchRequest(BaseModel):
    name_query: str


class FaceMatchResult(BaseModel):
    matched: bool
    person: Optional[WatchlistOut] = None
    confidence: float
    message: str
