# PDF/Word Export Stub
from fpdf import FPDF
from docx import Document

class Exporter:
    def export_to_pdf(self, proposal_data, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(40, 10, proposal_data.get('title', 'Proposal'))
        pdf.output(filename)
        return True

    def export_to_word(self, proposal_data, filename):
        doc = Document()
        doc.add_heading(proposal_data.get('title', 'Proposal'), 0)
        doc.save(filename)
        return True
