from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
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
from ..schemas import (
    AlertOut,
    CameraOut,
    CitizenReportCreate,
    CitizenReportOut,
    CrimeHotspot,
    DashboardStats,
    DispatchRequest,
    DispatchUnitOut,
    FaceMatchRequest,
    FaceMatchResult,
    IncidentCreate,
    IncidentOut,
    SensorOut,
    TrafficOut,
    VehiclePlateOut,
    WatchlistOut,
)
from ..services.ai_detection import match_face, simulate_cctv_analysis, simulate_sensor_trigger
from ..services.anpr_service import analyze_plates_in_image
from ..services.face_ai import analyze_faces_in_image, enroll_face_from_bytes
from ..services.analytics import get_crime_hotspots, get_dashboard_stats
from ..services.opencv_detection import (
    ALLOWED_IMAGE,
    ALLOWED_VIDEO,
    analyze_image_bytes,
    analyze_video_bytes,
)

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "system": "HSUSMS", "city": "Harare"}


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    return get_dashboard_stats(db)


@router.get("/dashboard/hotspots", response_model=List[CrimeHotspot])
def crime_hotspots(db: Session = Depends(get_db)):
    return get_crime_hotspots(db)


# --- Cameras / CCTV ---
@router.get("/cameras", response_model=List[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()


@router.post("/cameras/{camera_id}/analyze")
def analyze_camera(camera_id: int, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not cam:
        raise HTTPException(404, "Camera not found")
    return simulate_cctv_analysis(cam.name, cam.zone, cam.latitude, cam.longitude, db)


# --- Sensors / IoT ---
@router.get("/sensors", response_model=List[SensorOut])
def list_sensors(db: Session = Depends(get_db)):
    return db.query(Sensor).all()


@router.post("/sensors/{sensor_id}/trigger")
def trigger_sensor(sensor_id: int, db: Session = Depends(get_db)):
    result = simulate_sensor_trigger(db, sensor_id)
    if result is None:
        raise HTTPException(404, "Sensor not found")
    return result


# --- Incidents ---
@router.get("/incidents", response_model=List[IncidentOut])
def list_incidents(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Incident)
    if status:
        q = q.filter(Incident.status == status)
    return q.order_by(Incident.created_at.desc()).all()


@router.post("/incidents", response_model=IncidentOut)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.add(
        Alert(
            alert_type="incident",
            message=f"New incident: {incident.title}",
            zone=incident.zone,
            severity=incident.priority,
        )
    )
    db.commit()
    db.refresh(incident)
    return incident


@router.patch("/incidents/{incident_id}/resolve", response_model=IncidentOut)
def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident


# --- Emergency dispatch ---
@router.get("/dispatch/units", response_model=List[DispatchUnitOut])
def list_units(db: Session = Depends(get_db)):
    return db.query(DispatchUnit).all()


@router.post("/dispatch/assign", response_model=IncidentOut)
def assign_unit(req: DispatchRequest, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == req.incident_id).first()
    unit = db.query(DispatchUnit).filter(DispatchUnit.id == req.unit_id).first()
    if not incident or not unit:
        raise HTTPException(404, "Incident or unit not found")
    if unit.status != "available":
        raise HTTPException(400, f"Unit {unit.unit_name} is not available")
    incident.status = "dispatched"
    incident.assigned_unit = unit.unit_name
    unit.status = "busy"
    unit.current_incident_id = incident.id
    db.commit()
    db.refresh(incident)
    return incident


# --- Traffic ---
@router.get("/traffic", response_model=List[TrafficOut])
def list_traffic(db: Session = Depends(get_db)):
    return db.query(TrafficReading).order_by(TrafficReading.recorded_at.desc()).all()


# --- Facial recognition (OpenCV SFace) ---
def _watchlist_out(person: WatchlistPerson) -> WatchlistOut:
    return WatchlistOut(
        id=person.id,
        full_name=person.full_name,
        national_id=person.national_id,
        reason=person.reason,
        risk_level=person.risk_level,
        active=person.active,
        has_face_enrolled=bool(person.face_embedding),
        photo_file=person.photo_file,
    )


def _watchlist_gallery(db: Session):
    people = db.query(WatchlistPerson).filter(WatchlistPerson.active == True).all()
    return [
        (p.id, p.full_name, p.reason, p.risk_level, p.face_embedding)
        for p in people
    ]


@router.get("/watchlist", response_model=List[WatchlistOut])
def list_watchlist(db: Session = Depends(get_db)):
    return [_watchlist_out(p) for p in db.query(WatchlistPerson).filter(WatchlistPerson.active == True).all()]


@router.post("/watchlist/enroll")
async def enroll_watchlist_face(
    watchlist_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    person = db.query(WatchlistPerson).filter(WatchlistPerson.id == watchlist_id).first()
    if not person:
        raise HTTPException(404, "Watchlist person not found")
    data = await file.read()
    emb_json, meta = enroll_face_from_bytes(data)
    if not emb_json:
        raise HTTPException(400, meta.get("error", "Enrollment failed"))
    person.face_embedding = emb_json
    person.photo_file = file.filename
    db.commit()
    return {"success": True, "watchlist_id": watchlist_id, "full_name": person.full_name, **meta}


@router.post("/facial-recognition/analyze-image")
async def facial_analyze_image(
    file: UploadFile = File(...),
    create_incident: bool = Form(False),
    zone: str = Form("Zone 1 - CBD"),
    db: Session = Depends(get_db),
):
    data = await file.read()
    result = analyze_faces_in_image(data, _watchlist_gallery(db))
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Analysis failed"))

    if create_incident and result.get("watchlist_match"):
        match = result["matches"][0]
        incident = Incident(
            title=f"Facial Recognition: {match['full_name']}",
            description=f"Watchlist match ({match['confidence']:.0%}): {match['reason']}",
            incident_type="facial_match",
            source="Facial Recognition AI",
            zone=zone,
            latitude=-17.8292,
            longitude=31.0537,
            priority="high" if match["risk_level"] == "high" else "medium",
            status="open",
        )
        db.add(incident)
        db.add(
            Alert(
                alert_type="facial",
                message=f"Watchlist match: {match['full_name']}",
                zone=zone,
                severity="high",
            )
        )
        db.commit()
        db.refresh(incident)
        result["incident_id"] = incident.id

    return result


@router.post("/facial-recognition/match", response_model=FaceMatchResult)
def facial_match_text(req: FaceMatchRequest, db: Session = Depends(get_db)):
    """Legacy text search — use /facial-recognition/analyze-image for real AI."""
    return match_face(db, req.name_query)


# --- ANPR (Number Plate Recognition) ---
@router.get("/anpr/vehicles", response_model=List[VehiclePlateOut])
def list_vehicle_plates(db: Session = Depends(get_db)):
    return db.query(VehiclePlate).all()


@router.post("/anpr/analyze-image")
async def anpr_analyze_image(
    file: UploadFile = File(...),
    create_incident: bool = Form(False),
    zone: str = Form("Zone 2 - Intersections"),
    db: Session = Depends(get_db),
):
    data = await file.read()
    vehicles = db.query(VehiclePlate).all()
    vehicle_db = [(v.plate_number, v.owner_name, v.status, v.notes) for v in vehicles]
    try:
        result = analyze_plates_in_image(data, vehicle_db)
    except Exception as e:
        raise HTTPException(500, f"ANPR engine error: {e}") from e
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Analysis failed"))

    if create_incident and result.get("alert_count", 0) > 0:
        alert_plates = [d["plate_text"] for d in result["detections"] if d.get("alert")]
        incident = Incident(
            title=f"ANPR Alert: {', '.join(alert_plates)}",
            description=result["message"],
            incident_type="anpr_alert",
            source="ANPR AI",
            zone=zone,
            latitude=-17.8250,
            longitude=31.0500,
            priority="high",
            status="open",
        )
        db.add(incident)
        db.add(Alert(alert_type="anpr", message=result["message"], zone=zone, severity="high"))
        db.commit()
        db.refresh(incident)
        result["incident_id"] = incident.id

    return result


# --- Citizen reports ---
@router.get("/citizen/reports", response_model=List[CitizenReportOut])
def list_reports(db: Session = Depends(get_db)):
    return db.query(CitizenReport).order_by(CitizenReport.created_at.desc()).all()


@router.post("/citizen/reports", response_model=CitizenReportOut)
def submit_report(payload: CitizenReportCreate, db: Session = Depends(get_db)):
    report = CitizenReport(**payload.model_dump())
    incident = Incident(
        title=f"Citizen Report: {payload.report_type}",
        description=payload.description,
        incident_type=payload.report_type,
        source="Citizen App",
        zone="Citizen Reported",
        latitude=payload.latitude,
        longitude=payload.longitude,
        priority="medium" if payload.report_type != "emergency" else "high",
        status="open",
    )
    db.add(incident)
    db.flush()
    report.incident_id = incident.id
    report.status = "linked"
    db.add(report)
    db.add(
        Alert(
            alert_type="citizen",
            message=f"Citizen report: {payload.report_type}",
            zone="Citizen Reported",
            severity="high" if payload.report_type == "emergency" else "medium",
        )
    )
    db.commit()
    db.refresh(report)
    return report


# --- Alerts ---
@router.get("/alerts", response_model=List[AlertOut])
def list_alerts(acknowledged: bool | None = None, db: Session = Depends(get_db)):
    q = db.query(Alert)
    if acknowledged is not None:
        q = q.filter(Alert.acknowledged == acknowledged)
    return q.order_by(Alert.created_at.desc()).all()


@router.patch("/alerts/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert


# --- OpenCV Vision Analysis ---
@router.post("/vision/analyze-image")
async def vision_analyze_image(
    file: UploadFile = File(...),
    create_incident: bool = Form(False),
    zone: str = Form("Zone 1 - CBD"),
    db: Session = Depends(get_db),
):
    suffix = "." + (file.filename or "upload.jpg").rsplit(".", 1)[-1].lower()
    if suffix not in ALLOWED_IMAGE:
        raise HTTPException(400, f"Unsupported image type. Allowed: {ALLOWED_IMAGE}")
    data = await file.read()
    result = analyze_image_bytes(data, file.filename or "upload.jpg")
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Analysis failed"))

    if create_incident and result.get("motion_detected"):
        incident = Incident(
            title="OpenCV: Motion detected in uploaded image",
            description=result["message"],
            incident_type="motion_detection",
            source="OpenCV Vision",
            zone=zone,
            latitude=-17.8292,
            longitude=31.0537,
            priority="medium",
            status="open",
        )
        db.add(incident)
        db.add(Alert(alert_type="vision", message=result["message"], zone=zone, severity="medium"))
        db.commit()
        db.refresh(incident)
        result["incident_id"] = incident.id

    return result


@router.post("/vision/analyze-video")
async def vision_analyze_video(
    file: UploadFile = File(...),
    create_incident: bool = Form(False),
    zone: str = Form("Zone 1 - CBD"),
    db: Session = Depends(get_db),
):
    suffix = "." + (file.filename or "upload.mp4").rsplit(".", 1)[-1].lower()
    if suffix not in ALLOWED_VIDEO:
        raise HTTPException(400, f"Unsupported video type. Allowed: {ALLOWED_VIDEO}")
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(400, "Video must be under 50MB")
    result = analyze_video_bytes(data, file.filename or "upload.mp4")
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Analysis failed"))

    if create_incident and result.get("motion_detected"):
        incident = Incident(
            title="OpenCV: Motion detected in uploaded video",
            description=result["message"],
            incident_type="motion_detection",
            source="OpenCV Vision",
            zone=zone,
            latitude=-17.8292,
            longitude=31.0537,
            priority="high" if result.get("motion_events", 0) > 3 else "medium",
            status="open",
        )
        db.add(incident)
        db.add(Alert(alert_type="vision", message=result["message"], zone=zone, severity="high"))
        db.commit()
        db.refresh(incident)
        result["incident_id"] = incident.id

    return result
