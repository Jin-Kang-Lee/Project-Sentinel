import pandas as pd
import os
import random
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_FOLDER = "synthetic_pdfs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def generate_pdfs():
    # Load the data we generated in Step 1
    try:
        df_clients = pd.read_csv("synthetic_clients_master.csv")
        df_txns = pd.read_csv("synthetic_transaction_log.csv")
    except FileNotFoundError:
        print("❌ Error: CSV files not found. Please run data_generator.py first.")
        return

    print(f"📄 Creating PDFs for {len(df_clients)} clients...")

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#003366"))

    for _, client in df_clients.iterrows():
        c_id = client['Client_ID']
        c_name = client['Name']
        
        # Filter transactions for this specific client
        c_txns = df_txns[df_txns['Client_ID'] == c_id]
        
        if c_txns.empty: continue

        pdf_name = os.path.join(OUTPUT_FOLDER, f"Statement_{c_id}.pdf")
        doc = SimpleDocTemplate(pdf_name, pagesize=A4)
        elements = []

        # Header & Info
        elements.append(Paragraph("DBS (Digital Bank Simulation) - eStatement", header_style))
        elements.append(Spacer(1, 12))
        
        client_info = f"""
        <b>Customer Name:</b> {c_name}<br/>
        <b>Account Number:</b> {random.randint(1000000000, 9999999999)}<br/>
        <b>Date:</b> {datetime.now().strftime('%d %b %Y')}
        """
        elements.append(Paragraph(client_info, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Table Data
        data = [['Date', 'Description', 'Amount', 'Type', 'Balance']]
        
        for _, txn in c_txns.iterrows():
            data.append([
                txn['Date'], 
                txn['Description'], 
                f"${txn['Amount']:,.2f}", 
                txn['Type'],
                f"${txn['Balance']:,.2f}"
            ])

        # Table Styling
        t = Table(data, colWidths=[65, 190, 70, 50, 70])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (2,1), (-1,-1), 'RIGHT'), # Align amounts right
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("End of Statement. Computer Generated.", styles['Italic']))

        doc.build(elements)

    print(f"🎉 Success! Check the '{OUTPUT_FOLDER}' folder.")

if __name__ == "__main__":
    generate_pdfs()