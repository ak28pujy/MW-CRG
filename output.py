import os
from datetime import date

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph

OUTPUT_PATH = './output/'


def generate_output(company, full_outputs, summary_as_txt, summary_as_pdf, report_as_txt, report_as_pdf,
                    response_content):
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    if summary_as_txt:
        write_content_to_txt(company, full_outputs, 'Summary')
        write_content_to_docx(company, full_outputs, 'Summary')
    if summary_as_pdf:
        write_content_to_pdf(company, full_outputs, 'Summary')
    if report_as_txt:
        write_content_to_txt(company, response_content, 'Report')
        write_content_to_docx(company, response_content, 'Report')
    if report_as_pdf:
        write_content_to_pdf(company, response_content, 'Report')


def write_content_to_txt(company, content, file_type):
    file_path = get_file_path(file_type, company) + '.txt'
    try:
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(str(content))
    except PermissionError:
        print(f"\nNo permission to write the .txt file in the path: {file_path}.")
    except Exception as e:
        print(f"\nThere was a problem saving the .txt file: {e}")


def write_content_to_docx(company, content, file_type):
    file_path = get_file_path(file_type, company) + '.docx'
    try:
        doc = Document()
        doc.add_paragraph(str(content))
        doc.save(file_path)
    except PermissionError:
        print(f"\nNo permission to write the .docx file in the path: {file_path}.")
    except Exception as e:
        print(f"\nThere was a problem saving the .docx file: {e}")


def write_content_to_pdf(company, content, file_type):
    file_path = get_file_path(file_type, company) + '.pdf'
    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch,
                                bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = []
        for para_text in content.split('\n'):
            if not para_text.strip():
                para_text = '\u00A0'
            story.append(Paragraph(para_text, styles["Normal"]))
        doc.build(story)
    except PermissionError:
        print(f"\nNo permission to write the .pdf file in the path: {file_path}.")
    except Exception as e:
        print(f"\nThere was a problem saving the .pdf file: {e}")


def get_file_path(file_type, company):
    return f'{OUTPUT_PATH}{date.today()} - {company} - {file_type}'
