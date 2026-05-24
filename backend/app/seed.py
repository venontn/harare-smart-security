"""Seed Harare Smart Urban Security System with realistic demo data."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .models import (
    Alert,
    Camera,
    CitizenReport,
    DispatchUnit,
    Incident,
    Sensor,
    TrafficReading,
    VehiclePlate,
    WatchlistPerson,
)

# Harare approximate coordinates (CBD, Samora Machel, etc.)
HARARE_CBD = (-17.8292, 31.0537)


def seed_database(db: Session) -> None:
    if db.query(VehiclePlate).count() == 0:
        db.add_all([
            VehiclePlate(plate_number="AEA 1234", owner_name="Unknown", vehicle_type="sedan", status="stolen", notes="Reported stolen CBD"),
            VehiclePlate(plate_number="AFG 8891", owner_name="T. Muzenda", vehicle_type="pickup", status="wanted", notes="Traffic violations / evasion"),
            VehiclePlate(plate_number="ADB 4521", owner_name="City Council Fleet", vehicle_type="utility", status="registered", notes="Municipal vehicle"),
            VehiclePlate(plate_number="AEM 1102", owner_name="Private", vehicle_type="suv", status="registered", notes=""),
        ])
        db.commit()

    if db.query(Camera).count() > 0:
        return

    cameras = [
        Camera(name="CBD Samora Junction", zone="Zone 1 - CBD", latitude=-17.8254, longitude=31.0502, camera_type="PTZ", status="online"),
        Camera(name="Robert Mugabe Rd Camera 12", zone="Zone 1 - CBD", latitude=-17.8310, longitude=31.0488, camera_type="ANPR", status="online"),
        Camera(name="Eastgate Mall Entrance", zone="Zone 1 - CBD", latitude=-17.8298, longitude=31.0589, camera_type="CCTV", status="online"),
        Camera(name="Rotten Row & Nelson Mandela", zone="Zone 2 - Intersections", latitude=-17.8201, longitude=31.0421, camera_type="Traffic", status="online"),
        Camera(name="Borrowdale Brook Intersection", zone="Zone 2 - Intersections", latitude=-17.7988, longitude=31.0745, camera_type="Traffic", status="online"),
        Camera(name="Avondale Shopping Centre", zone="Zone 3 - Residential", latitude=-17.8012, longitude=31.0312, camera_type="CCTV", status="online"),
        Camera(name="Greendale Police Post", zone="Zone 3 - Residential", latitude=-17.8156, longitude=31.0891, camera_type="Body-worn hub", status="online"),
        Camera(name="Workington Industrial Gate", zone="Zone 4 - Industrial", latitude=-17.8542, longitude=31.0123, camera_type="Access Control", status="online"),
        Camera(name="Mbare Musika Terminus", zone="Zone 5 - Public Transport", latitude=-17.8689, longitude=31.0345, camera_type="Crowd", status="online"),
        Camera(name="Parirenyatwa Hospital Zone", zone="Zone 5 - Public Transport", latitude=-17.8089, longitude=31.0234, camera_type="CCTV", status="offline"),
        Camera(name="Parliament Building Perimeter", zone="Zone 6 - Government", latitude=-17.7998, longitude=31.0523, camera_type="Biometric", status="online"),
        Camera(name="City Council HQ", zone="Zone 6 - Government", latitude=-17.8278, longitude=31.0498, camera_type="CCTV", status="online"),
    ]
    db.add_all(cameras)

    sensors = [
        Sensor(name="CBD Motion Grid A", sensor_type="motion", zone="Zone 1 - CBD", latitude=-17.8280, longitude=31.0510, last_value=0.0, unit="trigger"),
        Sensor(name="Gunshot Acoustic CBD", sensor_type="gunshot", zone="Zone 1 - CBD", latitude=-17.8300, longitude=31.0520, last_value=12.0, unit="dB"),
        Sensor(name="Fire Sensor Eastgate", sensor_type="fire", zone="Zone 1 - CBD", latitude=-17.8295, longitude=31.0590, last_value=0.0, unit="ppm"),
        Sensor(name="Air Quality Samora", sensor_type="air_quality", zone="Zone 1 - CBD", latitude=-17.8260, longitude=31.0505, last_value=68.0, unit="AQI"),
        Sensor(name="Flood Sensor Mukuvisi", sensor_type="flood", zone="Zone 3 - Residential", latitude=-17.8400, longitude=31.0600, last_value=0.2, unit="m"),
        Sensor(name="Noise Sensor Mbare", sensor_type="noise", zone="Zone 5 - Public Transport", latitude=-17.8690, longitude=31.0350, last_value=78.0, unit="dB"),
        Sensor(name="Smart Parking Avondale", sensor_type="parking", zone="Zone 3 - Residential", latitude=-17.8015, longitude=31.0315, last_value=34.0, unit="%"),
    ]
    db.add_all(sensors)

    units = [
        DispatchUnit(unit_name="ZRP Patrol Alpha-1", agency="Zimbabwe Republic Police", unit_type="patrol", latitude=-17.8260, longitude=31.0500, status="available"),
        DispatchUnit(unit_name="ZRP Traffic Unit T-3", agency="Zimbabwe Republic Police", unit_type="traffic", latitude=-17.8220, longitude=31.0440, status="available"),
        DispatchUnit(unit_name="Ambulance A-07", agency="Harare Ambulance Services", unit_type="ambulance", latitude=-17.8100, longitude=31.0400, status="available"),
        DispatchUnit(unit_name="Fire Engine F-02", agency="Harare Fire Brigade", unit_type="fire", latitude=-17.8350, longitude=31.0550, status="busy"),
        DispatchUnit(unit_name="Disaster Response D-1", agency="Civil Protection", unit_type="disaster", latitude=-17.8200, longitude=31.0600, status="available"),
    ]
    db.add_all(units)

    watchlist = [
        WatchlistPerson(full_name="John Moyo", national_id="63-1234567A12", reason="Theft suspect - CBD", risk_level="high"),
        WatchlistPerson(full_name="Sarah Chikwanha", national_id="", reason="Missing person", risk_level="medium"),
        WatchlistPerson(full_name="Tendai Ncube", national_id="58-9876543B45", reason="Vandalism repeat offender", risk_level="medium"),
    ]
    db.add_all(watchlist)

    now = datetime.utcnow()
    incidents = [
        Incident(title="Suspicious activity near bank", description="AI detected loitering pattern", incident_type="suspicious_activity", source="CCTV AI", zone="Zone 1 - CBD", latitude=-17.8285, longitude=31.0515, priority="medium", status="open", created_at=now - timedelta(minutes=12)),
        Incident(title="Traffic collision - minor", description="Two vehicle fender bender", incident_type="traffic_accident", source="Traffic Camera", zone="Zone 2 - Intersections", latitude=-17.8205, longitude=31.0425, priority="medium", status="dispatched", assigned_unit="ZRP Traffic Unit T-3", created_at=now - timedelta(minutes=28)),
        Incident(title="Market disturbance report", description="Crowd noise threshold exceeded", incident_type="public_disturbance", source="IoT Sensor", zone="Zone 5 - Public Transport", latitude=-17.8692, longitude=31.0348, priority="high", status="open", created_at=now - timedelta(minutes=5)),
        Incident(title="Resolved: Pickpocketing arrest", description="Suspect detained after facial match", incident_type="crime", source="Facial Recognition", zone="Zone 1 - CBD", latitude=-17.8290, longitude=31.0530, priority="high", status="resolved", resolved_at=now - timedelta(hours=2), created_at=now - timedelta(hours=3)),
    ]
    db.add_all(incidents)

    traffic = [
        TrafficReading(intersection="Samora / First Street", zone="Zone 2 - Intersections", vehicle_count=142, congestion_level="high", latitude=-17.8250, longitude=31.0500),
        TrafficReading(intersection="Borrowdale / Liberation Legacy", zone="Zone 2 - Intersections", vehicle_count=67, congestion_level="medium", latitude=-17.7990, longitude=31.0750),
        TrafficReading(intersection="Seke / Chitungwiza Rd", zone="Zone 2 - Intersections", vehicle_count=198, congestion_level="critical", latitude=-17.8650, longitude=31.0700),
        TrafficReading(intersection="Avondale / King George", zone="Zone 3 - Residential", vehicle_count=45, congestion_level="low", latitude=-17.8010, longitude=31.0310),
    ]
    db.add_all(traffic)

    reports = [
        CitizenReport(reporter_name="Anonymous", report_type="theft", description="Phone snatched near copacabana taxi rank", latitude=-17.8315, longitude=31.0470, status="pending"),
        CitizenReport(reporter_name="T. Muzenda", report_type="emergency", description="Medical emergency - person collapsed", latitude=-17.8085, longitude=31.0240, status="linked"),
    ]
    db.add_all(reports)

    alerts = [
        Alert(alert_type="motion", message="Motion detected in restricted zone - Parliament perimeter", zone="Zone 6 - Government", severity="high"),
        Alert(alert_type="congestion", message="Critical congestion on Seke Road corridor", zone="Zone 2 - Intersections", severity="medium"),
        Alert(alert_type="sensor", message="Noise level exceeded 75dB at Mbare Musika", zone="Zone 5 - Public Transport", severity="high"),
        Alert(alert_type="cctv", message="Camera offline: Parirenyatwa Hospital Zone", zone="Zone 5 - Public Transport", severity="low"),
    ]
    db.add_all(alerts)

    db.commit()
