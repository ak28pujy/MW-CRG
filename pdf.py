import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def text_to_pdf(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    left_margin = 1 * 72
    right_margin = 0.5 * 72
    indent = 0.0 * 72
    available_width = width - left_margin - right_margin
    cur_height = height - left_margin
    line_height = 12
    paragraph_spacing = 20
    for line in lines:
        if line.strip() == "":
            cur_height -= paragraph_spacing
        else:
            wrapped_line = textwrap.wrap(line, width=int(
                (available_width - indent) / 6))
            for i, segment in enumerate(wrapped_line):
                if cur_height <= left_margin:
                    c.showPage()
                    cur_height = height - left_margin
                x_margin = left_margin + indent if i != 0 else left_margin
                c.drawString(x_margin, cur_height, segment.strip())
                cur_height -= line_height
    c.save()
