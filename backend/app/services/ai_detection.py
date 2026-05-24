"""Simulated AI services for CCTV and facial recognition (demo)."""

import random
from typing import Optional

from sqlalchemy.orm import Session

from ..models import WatchlistPerson, Alert, Incident
from ..schemas import FaceMatchResult, WatchlistOut


def simulate_cctv_analysis(camera_name: str, zone: str, lat: float, lng: float, db: Session) -> dict:
    """Simulate AI detecting suspicious activity from a camera feed."""
    triggers = [
        ("suspicious_activity", "Unusual loitering detected", "medium"),
        ("crowd_gathering", "Crowd density above threshold", "medium"),
        ("traffic_violation", "Vehicle running red light detected", "low"),
        ("intrusion", "Perimeter breach detected", "high"),
    ]
    if random.random() > 0.35:
        return {"detected": False, "message": "No anomalies in current frame"}

    incident_type, desc, priority = random.choice(triggers)
    incident = Incident(
        title=f"AI Alert: {desc}",
        description=f"Automated detection from {camera_name}",
        incident_type=incident_type,
        source="CCTV AI",
        zone=zone,
        latitude=lat,
        longitude=lng,
        priority=priority,
        status="open",
    )
    db.add(incident)
    alert = Alert(
        alert_type="cctv_ai",
        message=f"{camera_name}: {desc}",
        zone=zone,
        severity=priority,
    )
    db.add(alert)
    db.commit()
    db.refresh(incident)
    return {
        "detected": True,
        "incident_id": incident.id,
        "incident_type": incident_type,
        "priority": priority,
        "message": desc,
    }


def match_face(db: Session, name_query: str) -> FaceMatchResult:
    """Simulate facial recognition against watchlist."""
    query = name_query.strip().lower()
    people = db.query(WatchlistPerson).filter(WatchlistPerson.active == True).all()
    for person in people:
        if query in person.full_name.lower():
            confidence = round(random.uniform(0.87, 0.98), 2)
            return FaceMatchResult(
                matched=True,
                person=WatchlistOut.model_validate(person),
                confidence=confidence,
                message=f"Watchlist match: {person.full_name} ({confidence * 100:.0f}% confidence)",
            )
    return FaceMatchResult(
        matched=False,
        person=None,
        confidence=round(random.uniform(0.1, 0.4), 2),
        message="No watchlist match found",
    )


def simulate_sensor_trigger(db: Session, sensor_id: int) -> Optional[dict]:
    from ..models import Sensor

    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        return None

    thresholds = {
        "gunshot": (80, "Gunshot acoustic signature detected", "critical"),
        "fire": (50, "Fire/smoke threshold exceeded", "critical"),
        "flood": (1.5, "Flood water level rising", "high"),
        "noise": (85, "Noise disturbance detected", "medium"),
        "motion": (1, "Motion in secured area", "medium"),
    }
    cfg = thresholds.get(sensor.sensor_type)
    if not cfg:
        return {"triggered": False, "message": "Sensor reading normal"}

    threshold, msg, priority = cfg
    import random
    sensor.last_value = round(random.uniform(threshold, threshold + 20), 1)
    if sensor.last_value < threshold and sensor.sensor_type != "motion":
        return {"triggered": False, "message": "Sensor reading normal"}

    incident = Incident(
        title=f"IoT Alert: {sensor.name}",
        description=msg,
        incident_type=sensor.sensor_type,
        source="IoT Sensor",
        zone=sensor.zone,
        latitude=sensor.latitude,
        longitude=sensor.longitude,
        priority=priority,
        status="open",
    )
    db.add(incident)
    db.add(Alert(alert_type="sensor", message=msg, zone=sensor.zone, severity=priority))
    db.commit()
    return {"triggered": True, "incident_id": incident.id, "message": msg, "priority": priority}
