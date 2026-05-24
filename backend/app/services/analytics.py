from collections import Counter
from typing import List

from sqlalchemy.orm import Session

from ..models import Camera, DispatchUnit, Incident, Sensor, CitizenReport, Alert
from ..schemas import CrimeHotspot, DashboardStats


def get_dashboard_stats(db: Session) -> DashboardStats:
    active = db.query(Incident).filter(Incident.status.in_(["open", "dispatched", "in_progress"])).count()
    critical = db.query(Incident).filter(
        Incident.status.in_(["open", "dispatched", "in_progress"]),
        Incident.priority == "critical",
    ).count()
    return DashboardStats(
        active_incidents=active,
        open_alerts=db.query(Alert).filter(Alert.acknowledged == False).count(),
        cameras_online=db.query(Camera).filter(Camera.status == "online").count(),
        sensors_active=db.query(Sensor).filter(Sensor.status == "active").count(),
        units_available=db.query(DispatchUnit).filter(DispatchUnit.status == "available").count(),
        citizen_reports_pending=db.query(CitizenReport).filter(CitizenReport.status == "pending").count(),
        critical_incidents=critical,
        zones_monitored=6,
    )


def get_crime_hotspots(db: Session) -> List[CrimeHotspot]:
    incidents = db.query(Incident).all()
    by_zone: dict[str, list] = {}
    for inc in incidents:
        by_zone.setdefault(inc.zone, []).append(inc)

    hotspots = []
    for zone, items in by_zone.items():
        types = Counter(i.incident_type for i in items)
        dominant = types.most_common(1)[0][0] if types else "none"
        count = len(items)
        risk = min(100.0, count * 18.5 + (10 if any(i.priority in ("high", "critical") for i in items) else 0))
        hotspots.append(
            CrimeHotspot(zone=zone, incident_count=count, dominant_type=dominant, risk_score=round(risk, 1))
        )
    return sorted(hotspots, key=lambda h: h.risk_score, reverse=True)
