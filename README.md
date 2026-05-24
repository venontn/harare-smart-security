# Harare Smart Urban Security and Monitoring System (HSUSMS)

**Author:** Venon Takunda Nyadombo

Integrated smart city security platform prototype for Harare, Zimbabwe — Central Command & Control Center with CCTV, IoT, AI analytics, emergency dispatch, traffic monitoring, facial recognition, and citizen reporting.

## Architecture

```
Cameras / IoT / Citizen App  →  API (FastAPI)  →  SQLite Database
                                      ↓
                         Command Center Dashboard (Leaflet GIS)
```

## Modules Implemented

| Module | Features |
|--------|----------|
| Smart CCTV | 12 cameras across 6 zones, AI scan simulation |
| IoT Sensors | Motion, gunshot, fire, flood, noise, parking |
| Incidents | Create, list, resolve, GIS mapping |
| Emergency Dispatch | Assign police/ambulance/fire units |
| Traffic | Congestion readings per intersection |
| Facial Recognition AI | OpenCV YuNet + SFace embedding match |
| ANPR | EasyOCR plate read + stolen/wanted vehicle DB |
| Citizen Reporting | Mobile/web form → auto-incident |
| Crime Analytics | Hotspot risk scores by zone |
| Alerts | Real-time alert queue with acknowledge |

## GitHub & Live Hosting

**One-command publish** (after first-time `gh auth login`):

```powershell
.\publish.ps1
```

Then connect the repo on [Render](https://dashboard.render.com) → **New Blueprint** → select `harare-smart-security`.  
Full steps: [DEPLOY.md](DEPLOY.md)

---

## Quick Start (Windows)

```powershell
cd C:\Users\PC\Projects\harare-smart-security
.\run.ps1
```

Open **http://127.0.0.1:8000** in your browser.

### Manual start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: **http://127.0.0.1:8000/docs**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System status |
| GET | `/api/dashboard/stats` | Live KPIs |
| GET | `/api/dashboard/hotspots` | Crime hotspot analytics |
| GET | `/api/cameras` | List CCTV cameras |
| POST | `/api/cameras/{id}/analyze` | Run AI detection on feed |
| GET | `/api/sensors` | List IoT sensors |
| POST | `/api/sensors/{id}/trigger` | Simulate sensor alert |
| GET | `/api/incidents` | List incidents |
| POST | `/api/incidents` | Create incident |
| PATCH | `/api/incidents/{id}/resolve` | Resolve incident |
| GET | `/api/dispatch/units` | Emergency units |
| POST | `/api/dispatch/assign` | Dispatch unit to incident |
| GET | `/api/traffic` | Traffic congestion data |
| POST | `/api/facial-recognition/match` | Watchlist facial match |
| POST | `/api/citizen/reports` | Submit citizen report |

## Project Structure

```
harare-smart-security/
├── backend/
│   ├── app/
│   │   ├── api/routes.py      # REST API
│   │   ├── services/          # AI & analytics
│   │   ├── models.py          # Database models
│   │   ├── seed.py            # Harare demo data
│   │   └── main.py            # Application entry
│   └── requirements.txt
├── frontend/
│   ├── index.html             # Command center UI
│   ├── css/styles.css
│   └── js/app.js
├── data/                      # SQLite database (auto-created)
├── run.ps1
└── README.md
```

## Demo Usage

1. **Command Center** — View map with cameras (blue), sensors (purple), incidents (red), units (green).
2. **AI CCTV Scan** — CCTV tab → click **AI Scan** on any camera to simulate detection.
3. **OpenCV Vision** — OpenCV tab → upload an image or video for real motion detection.
4. **IoT** — Sensors tab → **Simulate** to trigger gunshot/fire/noise alerts.
5. **Dispatch** — Enter incident ID `1` and unit ID `1`, click **Assign Unit**.
6. **Facial ID** — Search `John Moyo` for a watchlist match.
7. **Citizen Report** — Submit a crime or emergency report; it creates an incident automatically.

## Citizen Mobile App (Flutter)

```powershell
cd mobile\hsusms_citizen
flutter pub get
flutter run
```

Configure API URL in `lib/services/api_service.dart` (see `mobile/hsusms_citizen/README.md`).

**Web fallback (no Flutter):** http://127.0.0.1:8000/citizen.html

## System Documentation (PDF)

```powershell
cd docs
..\backend\.venv\Scripts\python generate_pdf.py
```

Output: `docs/HSUSMS_System_Documentation.pdf`  
Full markdown: `docs/SYSTEM_DOCUMENTATION.md`

## Technologies

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** HTML/CSS/JavaScript, Leaflet (OpenStreetMap)
- **AI (demo):** Simulated detection (replace with OpenCV/TensorFlow in production)

## Production Roadmap

- Replace simulated AI with OpenCV / TensorFlow models
- PostgreSQL + Redis for scale
- Real RTSP camera streams (Hikvision / Milestone)
- LoRaWAN IoT gateway integration
- Role-based auth (ZRP, Fire, Council)
- 5G/fiber edge nodes per zone

## License

Academic / demonstration project for Harare smart city security research.

**Author:** Venon Takunda Nyadombo
