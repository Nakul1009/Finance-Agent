import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from typing import Dict, Any

class ReportGenerator:
    @staticmethod
    def generate_pdf_report(analytics_data: Dict[str, Any], doc_filename: str, executive_summary: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()
        story = []

        # Custom Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a')
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748b')
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#334155')
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#94a3b8')
        )

        # Header
        story.append(Paragraph("FinBank AI — Financial Document Intelligence Report", title_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Document Analyzed: <b>{doc_filename}</b> | Generated automatically by FinBank AI", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

        # Executive Summary
        story.append(Paragraph("1. Executive Summary", section_heading))
        story.append(Paragraph(executive_summary, body_style))
        story.append(Spacer(1, 10))

        # Metrics Summary Table
        story.append(Paragraph("2. Financial Metrics Summary", section_heading))
        metrics_table_data = [
            [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style)],
            [Paragraph("Total Income", body_style), f"₹{analytics_data.get('total_income', 0):,.2f}", Paragraph("Total Expenses", body_style), f"₹{analytics_data.get('total_expenses', 0):,.2f}"],
            [Paragraph("Net Cash Flow", body_style), f"₹{analytics_data.get('net_cash_flow', 0):,.2f}", Paragraph("Savings Rate", body_style), f"{analytics_data.get('savings_rate', 0):.1f}%"],
            [Paragraph("Transaction Count", body_style), str(analytics_data.get('transaction_count', 0)), Paragraph("Expense-to-Income", body_style), f"{analytics_data.get('expense_to_income_ratio', 0):.1f}%"],
        ]
        t = Table(metrics_table_data, colWidths=[130, 130, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

        # Top Categories
        story.append(Paragraph("3. Category Breakdown", section_heading))
        cat_data = [[Paragraph("<b>Category</b>", body_style), Paragraph("<b>Amount (₹)</b>", body_style), Paragraph("<b>Share (%)</b>", body_style)]]
        for c in analytics_data.get('top_categories', [])[:6]:
            cat_data.append([c['category'], f"₹{c['amount']:,.2f}", f"{c['percentage']:.1f}%"])
        if len(cat_data) > 1:
            t_cat = Table(cat_data, colWidths=[200, 160, 160])
            t_cat.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t_cat)
        story.append(Spacer(1, 10))

        # Financial Assessment
        assess = analytics_data.get('assessment', {})
        story.append(Paragraph("4. Financial Assessment & Commitments", section_heading))
        rating_color = colors.HexColor('#16a34a') if assess.get('rating') == 'Good' else (colors.HexColor('#d97706') if assess.get('rating') == 'Moderate' else colors.HexColor('#dc2626'))
        
        story.append(Paragraph(f"Financial Stability Rating: <b><font color='{rating_color.hexval()}'>{assess.get('rating', 'N/A')}</font></b>", ParagraphStyle('Rating', parent=body_style, fontSize=11, leading=15)))
        story.append(Paragraph(assess.get('summary_explanation', ''), body_style))
        story.append(Spacer(1, 6))

        # Detected Anomalies
        anoms = analytics_data.get('anomalies', [])
        if anoms:
            story.append(Paragraph("5. Detected Financial Patterns & Anomalies", section_heading))
            for a in anoms[:5]:
                story.append(Paragraph(f"• <b>{a['title']}</b>: {a['description']}", body_style))
                story.append(Spacer(1, 3))

        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8))
        story.append(Paragraph("<b>Disclaimer:</b> This application provides AI-assisted financial analysis and does not provide financial, legal, or lending advice.", disclaimer_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
