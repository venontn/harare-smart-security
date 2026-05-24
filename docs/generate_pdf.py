"""Generate HSUSMS system documentation PDF from structured content."""

from pathlib import Path

from fpdf import FPDF

OUTPUT = Path(__file__).parent / "HSUSMS_System_Documentation.pdf"


class HsusmsPdf(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 50, 90)
        self.cell(0, 8, "HSUSMS - Harare Smart Urban Security System", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, title: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 40, 80)
        self.ln(4)
        self.multi_cell(0, 8, title)
        self.ln(2)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text)
        self.ln(2)


def build_pdf():
    pdf = HsusmsPdf()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 35, 75)
    pdf.cell(0, 12, "System Documentation", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Harare Smart Urban Security and Monitoring System (HSUSMS)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Version 1.0 - Emerging Smart City Security Platform", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Author: Venon Takunda Nyadombo", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    sections = [
        (
            "1. Executive Summary",
            "HSUSMS integrates CCTV surveillance, IoT sensors, AI analytics, emergency dispatch, "
            "traffic monitoring, facial recognition (demo), citizen mobile reporting, and OpenCV motion "
            "detection into a Central Command and Control Center for Harare, Zimbabwe.",
        ),
        (
            "2. System Aim",
            "To design a centralized smart urban security system that enhances public safety, improves "
            "emergency response, supports law enforcement, and contributes to smart city development.",
        ),
        (
            "3. Architecture Layers",
            "1) Data Collection: cameras, sensors, citizen app\n"
            "2) Communication: REST API (FastAPI)\n"
            "3) Processing: AI simulation, OpenCV vision, analytics\n"
            "4) Command Center: web GIS dashboard\n"
            "5) Response: police, ambulance, fire, disaster units",
        ),
        (
            "4. Security Zones",
            "Zone 1 - CBD: CCTV, facial recognition\n"
            "Zone 2 - Intersections: traffic cameras\n"
            "Zone 3 - Residential: patrol, parking sensors\n"
            "Zone 4 - Industrial: access control\n"
            "Zone 5 - Public Transport: crowd, noise monitoring\n"
            "Zone 6 - Government: biometric perimeter",
        ),
        (
            "5. Core Modules",
            "Smart CCTV | IoT Sensors | Emergency Dispatch | Traffic Management | "
            "Facial Recognition (demo) | Citizen Reporting | OpenCV Vision | Crime Analytics",
        ),
        (
            "6. OpenCV Vision Module",
            "Upload images (JPG, PNG) or videos (MP4, AVI) for real motion detection using OpenCV. "
            "The system detects motion regions, returns annotated frames, and optionally creates incidents "
            "in the command center database.",
        ),
        (
            "7. Citizen Mobile App (Flutter)",
            "Features: emergency panic button, incident reporting with GPS, public alerts feed. "
            "Connects to the same REST API as the command center.",
        ),
        (
            "8. Functional Requirements",
            "Real-time monitoring, suspicious activity detection, traffic congestion, emergency alerts, "
            "secure data storage, GIS mapping, mobile access, crime statistics, multi-agency coordination - all implemented in prototype.",
        ),
        (
            "9. Non-Functional Requirements",
            "Scalable modular API, security via validation, 24/7 operation, privacy via anonymous reporting. "
            "Production: add JWT auth, PostgreSQL, encryption at rest, redundancy.",
        ),
        (
            "10. Technology Stack",
            "Backend: Python, FastAPI, SQLAlchemy, SQLite, OpenCV, NumPy\n"
            "Frontend: HTML/CSS/JS, Leaflet\n"
            "Mobile: Flutter\n"
            "Docs: Markdown, FPDF2",
        ),
        (
            "11. API Endpoints (Key)",
            "/api/health | /api/dashboard/stats | /api/cameras | /api/sensors | "
            "/api/incidents | /api/dispatch/assign | /api/vision/analyze-image | "
            "/api/vision/analyze-video | /api/citizen/reports",
        ),
        (
            "12. Smart City Impact",
            "KPIs: active incidents, response availability, sensor uptime, zone risk scores. "
            "Benefits: faster detection, evidence-based policing, citizen engagement. "
            "Risks: surveillance overreach (mitigate with governance), infrastructure gaps (phased rollout).",
        ),
        (
            "13. Implementation Phases",
            "Phase 1: CBD pilot (current)\n"
            "Phase 2: Intersections + IoT\n"
            "Phase 3: Zones 4-6\n"
            "Phase 4: Production RTSP, TensorFlow models, 5G edge",
        ),
        (
            "14. Conclusion",
            "HSUSMS provides a complete academic and technical foundation for evaluating how urban security "
            "technologies contribute to Harare's development as an emerging smart city.",
        ),
    ]

    for title, body in sections:
        pdf.chapter_title(title)
        pdf.body_text(body)

    pdf.add_page()
    pdf.chapter_title("Appendix: Running the System")
    pdf.body_text(
        "1. Start server: .\\run.ps1 from project root\n"
        "2. Open dashboard: http://127.0.0.1:8000\n"
        "3. API docs: http://127.0.0.1:8000/docs\n"
        "4. Flutter app: cd mobile\\hsusms_citizen && flutter run\n"
        "5. Regenerate this PDF: python docs\\generate_pdf.py"
    )

    pdf.output(str(OUTPUT))
    print(f"PDF written to: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
