def generer_pdf_ticket(data: dict) -> dict:
    try:
        from pathlib import Path
        from reportlab.pdfgen import canvas

        root = Path(__file__).resolve().parents[1]
        out_dir = root / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "ticket_az_turf_pro.pdf"

        ticket = data.get("ticket") or data.get("quinte") or []
        nums = [str(x.get("numero") if isinstance(x, dict) else x) for x in ticket]

        c = canvas.Canvas(str(path))
        c.setTitle("AZ Turf Pro - Ticket")
        c.drawString(50, 800, "AZ TURF PRO - TICKET")
        c.drawString(50, 770, " - ".join(nums) if nums else "Aucune sélection")
        c.save()

        return {"status": "success", "url_pdf": str(path)}
    except Exception as exc:
        return {"status": "error", "message": f"PDF indisponible: {exc}", "url_pdf": ""}
