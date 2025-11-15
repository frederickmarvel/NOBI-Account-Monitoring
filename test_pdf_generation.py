#!/usr/bin/env python3
"""
Test PDF Generation with Database Opening Balance
"""

import sys
sys.path.append('backend')

from database_service import DatabaseService
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import io

def generate_pdf_statement(wallet_address, opening_date, end_date, opening_balance, current_balance, transactions, network=None):
    """Generate PDF statement"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    if 'CustomTitle' not in styles:
        styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER, fontName='Helvetica-Bold'))
    
    elements = []
    
    # Title
    elements.append(Paragraph("BLOCKCHAIN ACCOUNT STATEMENT", styles['CustomTitle']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Header
    header_data = [
        ['Wallet:', wallet_address],
        ['Network:', network or 'All Networks'],
        ['Period:', f"{opening_date} to {end_date}"],
        ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Opening Balance
    elements.append(Paragraph(f"<b>OPENING BALANCE (as of {opening_date})</b>", styles['Heading2']))
    if opening_balance:
        balance_data = [['Token', 'Amount']]
        sorted_items = sorted(opening_balance.items(), key=lambda x: abs(x[1]), reverse=True)
        for token, amount in sorted_items[:15]:
            if amount != 0:
                balance_data.append([token[:25], f"{amount:,.6f}".rstrip('0').rstrip('.')])
        
        balance_table = Table(balance_data, colWidths=[3*inch, 2.5*inch])
        balance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(balance_table)
    else:
        elements.append(Paragraph("No balances", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Transactions
    elements.append(Paragraph(f"<b>TRANSACTIONS ({opening_date} to {end_date})</b>", styles['Heading2']))
    if transactions:
        tx_data = [['Date', 'Type', 'Amount', 'Token']]
        for tx in transactions[:50]:
            date = str(tx.get('transaction_date', ''))[:16]
            direction = str(tx.get('direction', '')).upper()[:3]
            amount = tx.get('amount')
            token = str(tx.get('token_symbol', ''))[:12]
            
            if amount:
                try:
                    amount_str = f"{float(amount):,.2f}"
                except:
                    amount_str = str(amount)[:15]
            else:
                amount_str = '-'
            
            tx_data.append([date, direction, amount_str, token])
        
        if len(transactions) > 50:
            tx_data.append(['...', '...', '...', f'+ {len(transactions) - 50} more'])
        
        tx_table = Table(tx_data, colWidths=[1.5*inch, 0.8*inch, 1.5*inch, 1.7*inch])
        tx_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(tx_table)
    else:
        elements.append(Paragraph("No transactions", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Closing Balance
    elements.append(Paragraph(f"<b>CLOSING BALANCE (as of {end_date})</b>", styles['Heading2']))
    if current_balance:
        balance_data = [['Token', 'Amount']]
        sorted_items = sorted(current_balance.items(), key=lambda x: abs(x[1]), reverse=True)
        for token, amount in sorted_items[:15]:
            if amount != 0:
                balance_data.append([token[:25], f"{amount:,.6f}".rstrip('0').rstrip('.')])
        
        balance_table = Table(balance_data, colWidths=[3*inch, 2.5*inch])
        balance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(balance_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def test_pdf_generation():
    """Test PDF generation with real data"""
    print("="*80)
    print("📄 TESTING PDF GENERATION WITH DATABASE")
    print("="*80)
    
    # Connect to database
    db = DatabaseService(
        host='217.216.110.33',
        port=3306,
        username='root',
        password='nobicuan888',
        database='nobi_wallet_tracker'
    )
    
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Test wallet
        wallet = "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc"
        start = "2025-03-01"
        end = "2025-10-01"
        network = "sol-mainnet"
        
        print(f"\n📊 Fetching data for wallet: {wallet}")
        print(f"   Period: {start} to {end}")
        print(f"   Network: {network}\n")
        
        # Get data
        opening = db.calculate_opening_balance(wallet, start, network=network)
        current = db.get_current_balance(wallet, end, network=network)
        transactions = db.get_transactions_in_period(wallet, start, end, network=network)
        
        print(f"✅ Data retrieved:")
        print(f"   Opening balance: {len(opening['balances'])} tokens")
        print(f"   Current balance: {len(current['balances'])} tokens")
        print(f"   Transactions: {len(transactions)}")
        
        # Generate PDF
        print(f"\n📄 Generating PDF...")
        pdf_bytes = generate_pdf_statement(
            wallet,
            start,
            end,
            opening['balances'],
            current['balances'],
            transactions,
            network
        )
        
        # Save PDF
        output_path = "/tmp/blockchain_statement.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"\n✅ PDF generated successfully!")
        print(f"   File: {output_path}")
        print(f"   Size: {len(pdf_bytes):,} bytes")
        print(f"\n💡 Open the PDF:")
        print(f"   open {output_path}")
        
    finally:
        db.disconnect()
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_pdf_generation()
