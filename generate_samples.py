import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def main():
    sample_dir = os.path.join(os.getcwd(), "sample_files")
    os.makedirs(sample_dir, exist_ok=True)
    print(f"Generating sample files in: {sample_dir}")

    # Data set 1: Tech Professional Statement (Q1 2026)
    data_1 = [
        {"Date": "2026-01-01", "Narration": "ACH SALARY CREDIT TECH GLOBAL LTD", "Ref No": "SAL20260101", "Debit": "", "Credit": "95000.00", "Balance": "135000.00"},
        {"Date": "2026-01-03", "Narration": "SWIGGY FOOD DELIVERY BANGALORE", "Ref No": "UPI1002341", "Debit": "540.00", "Credit": "", "Balance": "134460.00"},
        {"Date": "2026-01-05", "Narration": "HOUSE RENT TRANSFER TO LANDLORD", "Ref No": "NEFT1002342", "Debit": "25000.00", "Credit": "", "Balance": "109460.00"},
        {"Date": "2026-01-08", "Narration": "BESCOM ELECTRICITY BILL", "Ref No": "BILL202601", "Debit": "2150.00", "Credit": "", "Balance": "107310.00"},
        {"Date": "2026-01-12", "Narration": "AMAZON INDIA SHOPPING", "Ref No": "AMZ202601", "Debit": "4899.00", "Credit": "", "Balance": "102411.00"},
        {"Date": "2026-01-15", "Narration": "NETFLIX MONTHLY SUBSCRIPTION", "Ref No": "NFLX202601", "Debit": "649.00", "Credit": "", "Balance": "101762.00"},
        {"Date": "2026-01-20", "Narration": "ZERODHA MUTUAL FUND SIP", "Ref No": "SIP202601", "Debit": "20000.00", "Credit": "", "Balance": "81762.00"},
        {"Date": "2026-02-01", "Narration": "ACH SALARY CREDIT TECH GLOBAL LTD", "Ref No": "SAL20260201", "Debit": "", "Credit": "95000.00", "Balance": "176762.00"},
        {"Date": "2026-02-05", "Narration": "HOUSE RENT TRANSFER TO LANDLORD", "Ref No": "NEFT2002342", "Debit": "25000.00", "Credit": "", "Balance": "151762.00"},
        {"Date": "2026-02-10", "Narration": "AIRTEL BROADBAND RECHARGE", "Ref No": "BILL202602", "Debit": "1299.00", "Credit": "", "Balance": "150463.00"},
        {"Date": "2026-02-14", "Narration": "APPLE STORE ELECTRONICS PURCHASE", "Ref No": "POS20260214", "Debit": "64900.00", "Credit": "", "Balance": "85563.00"},
        {"Date": "2026-02-20", "Narration": "ZERODHA MUTUAL FUND SIP", "Ref No": "SIP202602", "Debit": "20000.00", "Credit": "", "Balance": "65563.00"},
        {"Date": "2026-03-01", "Narration": "ACH SALARY CREDIT TECH GLOBAL LTD", "Ref No": "SAL20260301", "Debit": "", "Credit": "95000.00", "Balance": "160563.00"},
        {"Date": "2026-03-05", "Narration": "HOUSE RENT TRANSFER TO LANDLORD", "Ref No": "NEFT3002342", "Debit": "25000.00", "Credit": "", "Balance": "135563.00"},
        {"Date": "2026-03-15", "Narration": "NETFLIX MONTHLY SUBSCRIPTION", "Ref No": "NFLX202603", "Debit": "649.00", "Credit": "", "Balance": "134914.00"},
        {"Date": "2026-03-20", "Narration": "ZERODHA MUTUAL FUND SIP", "Ref No": "SIP202603", "Debit": "20000.00", "Credit": "", "Balance": "114914.00"},
    ]

    # 1. Generate CSV
    df_1 = pd.DataFrame(data_1)
    csv_path = os.path.join(sample_dir, "sample_bank_statement.csv")
    df_1.to_csv(csv_path, index=False)
    print(f"Created: {csv_path}")

    # 2. Generate XLSX
    xlsx_path = os.path.join(sample_dir, "sample_bank_statement.xlsx")
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df_1.to_excel(writer, sheet_name='Account Statement', index=False)
    print(f"Created: {xlsx_path}")

    # 3. Generate HDFC Style PDF
    pdf_hdfc_path = os.path.join(sample_dir, "sample_hdfc_bank_statement.pdf")
    doc_hdfc = SimpleDocTemplate(pdf_hdfc_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), spaceAfter=6)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4B5563'), spaceAfter=12)
    
    story.append(Paragraph("HDFC BANK - ACCOUNT STATEMENT", title_style))
    story.append(Paragraph("Account Holder: Alex Morgan | Account No: 501002394810 | Period: Jan 2026 - Mar 2026", sub_style))
    story.append(Spacer(1, 10))

    table_data = [["Date", "Narration", "Chq/Ref No", "Withdrawal (Dr)", "Deposit (Cr)", "Closing Balance"]]
    for item in data_1:
        table_data.append([
            item["Date"],
            item["Narration"],
            item["Ref No"],
            item["Debit"],
            item["Credit"],
            item["Balance"]
        ])

    t = Table(table_data, colWidths=[65, 190, 85, 75, 75, 75])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t)
    doc_hdfc.build(story)
    print(f"Created: {pdf_hdfc_path}")

    # 4. Generate ICICI/SBI Style PDF (Dataset 2)
    data_2 = [
        {"Txn Date": "2026-01-02", "Details": "SALARY CREDITED FROM APEX SYSTEMS", "Ref": "SBI001293", "Withdrawal": "", "Deposit": "80000.00", "Balance": "110000.00"},
        {"Txn Date": "2026-01-04", "Details": "ZOMATO ONLINE ORDER", "Ref": "UPI88921", "Withdrawal": "450.00", "Deposit": "", "Balance": "109550.00"},
        {"Txn Date": "2026-01-06", "Details": "RENT CREDIT TRANSFER", "Ref": "UPI88922", "Withdrawal": "20000.00", "Deposit": "", "Balance": "89550.00"},
        {"Txn Date": "2026-01-10", "Details": "UBER INDIA SYSTEMS", "Ref": "UPI88923", "Withdrawal": "380.00", "Deposit": "", "Balance": "89170.00"},
        {"Txn Date": "2026-01-15", "Details": "AMAZON PAY UTILITIES", "Ref": "BILL9981", "Withdrawal": "1650.00", "Deposit": "", "Balance": "87520.00"},
        {"Txn Date": "2026-01-25", "Details": "ATM CASH WITHDRAWAL ICICI", "Ref": "ATM9912", "Withdrawal": "4000.00", "Deposit": "", "Balance": "83520.00"},
        {"Txn Date": "2026-02-02", "Details": "SALARY CREDITED FROM APEX SYSTEMS", "Ref": "SBI002293", "Withdrawal": "", "Deposit": "80000.00", "Balance": "163520.00"},
        {"Txn Date": "2026-02-06", "Details": "RENT CREDIT TRANSFER", "Ref": "UPI88924", "Withdrawal": "20000.00", "Deposit": "", "Balance": "143520.00"},
        {"Txn Date": "2026-02-18", "Details": "MAKE MY TRIP FLIGHT TICKETS", "Ref": "POS55412", "Withdrawal": "18500.00", "Deposit": "", "Balance": "125020.00"},
        {"Txn Date": "2026-03-02", "Details": "SALARY CREDITED FROM APEX SYSTEMS", "Ref": "SBI003293", "Withdrawal": "", "Deposit": "80000.00", "Balance": "205020.00"},
        {"Txn Date": "2026-03-06", "Details": "RENT CREDIT TRANSFER", "Ref": "UPI88925", "Withdrawal": "20000.00", "Deposit": "", "Balance": "185020.00"},
    ]

    pdf_sbi_path = os.path.join(sample_dir, "sample_sbi_bank_statement.pdf")
    doc_sbi = SimpleDocTemplate(pdf_sbi_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story2 = []

    story2.append(Paragraph("STATE BANK OF INDIA - STATEMENT OF ACCOUNT", title_style))
    story2.append(Paragraph("Account Holder: Priya Sharma | Account No: 33400192831 | Branch: MG Road Bangalore", sub_style))
    story2.append(Spacer(1, 10))

    table_data2 = [["Txn Date", "Details", "Ref No", "Debit Amount", "Credit Amount", "Balance"]]
    for item in data_2:
        table_data2.append([
            item["Txn Date"],
            item["Details"],
            item["Ref"],
            item["Withdrawal"],
            item["Deposit"],
            item["Balance"]
        ])

    t2 = Table(table_data2, colWidths=[65, 190, 85, 75, 75, 75])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284C7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F9FF')])
    ]))
    story2.append(t2)
    doc_sbi.build(story2)
    print(f"Created: {pdf_sbi_path}")

    print("\nAll 4 sample files successfully generated!")

if __name__ == "__main__":
    main()
