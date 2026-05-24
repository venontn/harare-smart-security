# HSUSMS System Documentation

**Harare Smart Urban Security and Monitoring System**  
Version 1.0 | Harare, Zimbabwe

---

## 1. Executive Summary

HSUSMS is an integrated smart city security platform designed for Harare as an emerging smart city. It unifies CCTV surveillance, IoT sensors, AI analytics, emergency dispatch, traffic monitoring, facial recognition (demo), citizen reporting, and OpenCV-based motion detection into a single Central Command and Control Center.

---

## 2. System Aim and Objectives

**Aim:** Design a centralized smart urban security system that enhances public safety, improves emergency response, supports law enforcement, and contributes to smart city development.

| # | Objective | Implementation |
|---|-----------|----------------|
| 1 | Monitor urban activities | 12 CCTV cameras across 6 zones |
| 2 | Detect criminal activities | AI simulation + OpenCV motion detection |
| 3 | Improve emergency response | Multi-agency dispatch module |
| 4 | Enhance traffic management | Traffic congestion readings |
| 5 | Integrate IoT sensors | 7 sensor types with alert triggers |
| 6 | Store and analyze data | SQLite + hotspot analytics |
| 7 | Evaluate smart city impact | KPI dashboard + documentation |

---

## 3. System Architecture

### 3.1 High-Level Layers

1. **Data Collection** — Cameras, IoT sensors, citizen mobile app  
2. **Communication** — REST API (HTTP/JSON), CORS-enabled  
3. **Processing** — AI simulation, OpenCV vision, analytics engine  
4. **Command Center** — Web dashboard with GIS (Leaflet)  
5. **Response** — Police, ambulance, fire, disaster units  

### 3.2 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend API | Python 3.13, FastAPI, SQLAlchemy |
| Database | SQLite |
| AI / Vision | OpenCV (motion detection), simulated ML |
| Frontend | HTML/CSS/JS, Leaflet maps |
| Mobile | Flutter (citizen app) |
| Documentation | Markdown, FPDF2 PDF export |

---

## 4. Security Zones

| Zone | Coverage | Technologies |
|------|----------|--------------|
| Zone 1 | Harare CBD | Smart CCTV, Facial Recognition |
| Zone 2 | Road Intersections | Traffic cameras, smart lights |
| Zone 3 | Residential | Patrol systems, parking sensors |
| Zone 4 | Industrial | Access control |
| Zone 5 | Public Transport | Crowd monitoring, noise sensors |
| Zone 6 | Government | Biometric perimeter |

---

## 5. Module Specifications

### 5.1 Smart CCTV Module

- **Inputs:** Live feeds (simulated), motion triggers  
- **Processes:** AI scan simulation, OpenCV upload analysis  
- **Outputs:** Security alerts, incident records  
- **API:** `GET /api/cameras`, `POST /api/cameras/{id}/analyze`

### 5.2 IoT Sensor Module

- **Sensor types:** motion, gunshot, fire, flood, noise, parking, air_quality  
- **API:** `GET /api/sensors`, `POST /api/sensors/{id}/trigger`

### 5.3 Emergency Dispatch Module

- **Agencies:** ZRP, Ambulance, Fire Brigade, Civil Protection  
- **API:** `GET /api/dispatch/units`, `POST /api/dispatch/assign`

### 5.4 Traffic Management Module

- **Metrics:** vehicle count, congestion level (low/medium/high/critical)  
- **API:** `GET /api/traffic`

### 5.5 Facial Recognition Module (Demo)

- **Process:** Watchlist name matching with confidence score  
- **API:** `POST /api/facial-recognition/match`, `GET /api/watchlist`

### 5.6 Citizen Interaction Module

- **Channels:** Flutter app, web form, REST API  
- **API:** `POST /api/citizen/reports`

### 5.7 OpenCV Vision Module

- **Image analysis:** Background subtraction, contour detection, annotated output  
- **Video analysis:** Frame differencing across sampled frames  
- **API:** `POST /api/vision/analyze-image`, `POST /api/vision/analyze-video`

---

## 6. Functional Requirements (Verified)

| ID | Requirement | Status |
|----|-------------|--------|
| FR1 | Capture real-time video footage | Simulated + upload analysis |
| FR2 | Detect suspicious activities | AI + OpenCV |
| FR3 | Identify wanted individuals | Watchlist demo |
| FR4 | Monitor traffic congestion | Traffic module |
| FR5 | Generate emergency alerts | Panic + dispatch |
| FR6 | Store surveillance data securely | SQLite persistence |
| FR7 | GIS incident mapping | Leaflet dashboard |
| FR8 | Mobile access | Flutter citizen app |
| FR9 | Crime statistics reports | Hotspot analytics |
| FR10 | Multi-agency coordination | Dispatch assignment |

---

## 7. Non-Functional Requirements

| Requirement | Approach |
|-------------|----------|
| Scalability | Modular API; migrate to PostgreSQL for production |
| Security | CORS, input validation; add JWT/RBAC for production |
| Availability | 24/7 local server; add redundancy in production |
| Real-time | 30s dashboard refresh; WebSocket optional |
| Privacy | Citizen anonymous reporting; governance recommendations |
| Disaster recovery | Database file backup; cloud replication recommended |

---

## 8. Data Model

**Entities:** Camera, Sensor, Incident, DispatchUnit, CitizenReport, WatchlistPerson, TrafficReading, Alert

**Incident lifecycle:** open → dispatched → in_progress → resolved

---

## 9. API Reference (Summary)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | System status |
| GET | /api/dashboard/stats | KPI metrics |
| GET | /api/dashboard/hotspots | Crime hotspots |
| POST | /api/vision/analyze-image | OpenCV image motion |
| POST | /api/vision/analyze-video | OpenCV video motion |
| POST | /api/citizen/reports | Citizen report |

Full interactive docs: `http://127.0.0.1:8000/docs`

---

## 10. Deployment Guide

```powershell
cd harare-smart-security
.\run.ps1
```

Generate PDF documentation:

```powershell
cd docs
..\backend\.venv\Scripts\python generate_pdf.py
```

---

## 11. Smart City Impact Evaluation

### 11.1 KPIs Tracked

- Active incidents and critical count  
- Emergency unit availability  
- Camera/sensor uptime  
- Citizen report response linkage  
- Zone-based risk scores  

### 11.2 Expected Benefits

- Faster incident detection and dispatch  
- Evidence-based patrol planning  
- Improved citizen participation  
- Foundation for city-wide smart services  

### 11.3 Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Surveillance overreach | Governance board, signage, audit logs |
| Infrastructure gaps | Phased rollout, solar/backup power |
| AI false positives | Human verification before enforcement |
| Cyber threats | Encryption, segmentation, pen testing |

---

## 12. Implementation Phases

| Phase | Scope |
|-------|-------|
| 1 | CBD pilot — CCTV + command center (current prototype) |
| 2 | Intersections + IoT expansion |
| 3 | City-wide zones 4–6 |
| 4 | Production AI, RTSP cameras, 5G edge nodes |

---

## 13. Conclusion

HSUSMS demonstrates a complete smart urban security architecture for Harare, integrating multiple technologies into one operational platform suitable for academic evaluation and phased real-world deployment.

---

*Document generated for the project: Design and Evaluation of an Integrated Smart Urban Security System for Harare as an Emerging Smart City.*

**Author:** Venon Takunda Nyadombo
