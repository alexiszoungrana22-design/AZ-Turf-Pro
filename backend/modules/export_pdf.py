from datetime import datetime
from pathlib import Path
import uuid

from config import EXPORT_DIR


def generer_pdf_ticket(data: dict) -> dict:
    """Génère un PDF simple et autonome du ticket transmis."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return {
            "status": "error",
            "message": "Le module reportlab est requis pour l'export PDF."
        }

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"ticket-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}.pdf"
    path = EXPORT_DIR / filename

    course = data.get("course") or {}
    tickets = data.get("tickets") or {}
    gratuit = tickets.get("gratuit") or {}
    premium = tickets.get("premium") or {}

    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setTitle("AZ Turf Pro - Ticket")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, y, "AZ Turf Pro")
    y -= 28
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, y, f"Course : {course.get('course', data.get('course', ''))}")
    y -= 18
    pdf.drawString(40, y, f"Hippodrome : {course.get('hippodrome', data.get('hippodrome', ''))}")
    y -= 18
    pdf.drawString(40, y, f"Date : {course.get('date', data.get('date', ''))}")
    y -= 30

    def ligne(label, value):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(40, y, label)
        pdf.setFont("Helvetica", 11)
        pdf.drawString(180, y, str(value))
        y -= 20
        if y < 60:
            pdf.showPage()
            y = height - 50

    ligne("Quinté gratuit", " - ".join(map(str, gratuit.get("quinte", []))))
    ligne("2 sur 4", " - ".join(map(str, gratuit.get("deux_sur_quatre", []))))
    ligne("Couple placé", " - ".join(map(str, gratuit.get("couple_place", []))))

    if premium:
        y -= 10
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(40, y, "Premium")
        y -= 22
        for cle in ("selection_quinte", "quinte", "quarte", "trio"):
            valeur = premium.get(cle)
            if valeur:
                ligne(cle.replace("_", " ").title(), " - ".join(map(str, valeur)) if isinstance(valeur, list) else valeur)

    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(40, 35, "Généré par AZ Turf Pro — document informatif.")
    pdf.save()

    return {
        "status": "success",
        "filename": filename,
        "url_pdf": f"/api/export/pdf/{filename}"
    }
