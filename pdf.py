import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def text_to_pdf(input_file, output_file):
    # Öffne die Eingabedatei und lies die Zeilen
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Erstelle ein neues PDF-Dokument mit A4-Größe
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter  # Hole die Standardseitengröße (A4)

    # Definiere Seitenränder (in Punkt, ReportLab verwendet 72 Punkte pro Zoll)
    left_margin = 1 * 72  # 1 Zoll linker Seitenrand
    right_margin = 0.5 * 72  # 0.5 Zoll rechter Seitenrand
    indent = 0.0 * 72  # 0.0 Zoll Einzug für Zeilenumbrüche
    # indent = 0.25 * 72  # 0.25 Zoll Einzug für Zeilenumbrüche

    # Berechne die verfügbare Breite innerhalb der Seitenränder
    available_width = width - left_margin - right_margin

    # Behalte die aktuelle Höhenposition im Auge. Starte am oberen Seitenrand minus dem Seitenrand
    cur_height = height - left_margin

    # Definiere eine Höhe für jede Zeile.
    line_height = 12

    # Definiere den Abstand für einen neuen Absatz
    paragraph_spacing = 20  # Platz für einen neuen Absatz hinzufügen

    # Gehe durch jede Zeile im Text
    for line in lines:
        # Wenn die Zeile leer ist, füge zusätzlichen Platz für einen neuen Absatz hinzu
        if line.strip() == "":
            cur_height -= paragraph_spacing
        else:
            # Wickel die Zeile so ein, dass sie innerhalb der verfügbaren Breite passt
            wrapped_line = textwrap.wrap(line, width=int(
                (available_width - indent) / 6))  # Passe den Teiler an, um die Zeilenlänge zu steuern
            # Gehe durch jedes Segment der umgebrochenen Zeile
            for i, segment in enumerate(wrapped_line):
                # Wenn wir am unteren Rand der Seite angekommen sind, erstelle eine neue Seite
                if cur_height <= left_margin:
                    c.showPage()
                    cur_height = height - left_margin
                # Füge einen Einzug hinzu, wenn es sich um eine gebrochene Zeile handelt
                x_margin = left_margin + indent if i != 0 else left_margin
                # Zeichne die Zeile auf das PDF
                c.drawString(x_margin, cur_height, segment.strip())
                # Bewege die aktuelle Höhe nach unten für die nächste Zeile
                cur_height -= line_height

    # Speichere das PDF-Dokument
    c.save()
