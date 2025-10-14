"""
PDF Report Generator
Creates professional account statements with USD and AED conversions
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import io
from typing import Dict, List


class PDFReportGenerator:
    """Generate PDF account statements with currency conversions"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e')
        ))
    
    def generate_account_statement(
        self,
        address: str,
        blockchain: str,
        transactions: List[Dict],
        balance: float,
        crypto_symbol: str,
        prices: Dict[str, float],
        date_range: Dict[str, str],
        token_balances: Dict[str, Dict] = None
    ) -> bytes:
        """
        Generate PDF account statement
        
        Args:
            address: Wallet address
            blockchain: Blockchain name
            transactions: List of transactions
            balance: Current balance in crypto
            crypto_symbol: Symbol (ETH, BTC, etc.)
            prices: {'usd': price, 'aed': price}
            date_range: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
            token_balances: Optional dict of token balances with prices
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Build document elements
        elements = []
        
        # Title
        title = Paragraph("BLOCKCHAIN ACCOUNT STATEMENT", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Account Information
        account_info = self._create_account_info_table(
            address, blockchain, balance, crypto_symbol, prices, date_range
        )
        elements.append(account_info)
        elements.append(Spacer(1, 0.2*inch))
        
        # Token Balances (if available)
        if token_balances:
            token_heading = Paragraph("Token Holdings", self.styles['CustomHeading'])
            elements.append(token_heading)
            elements.append(Spacer(1, 0.1*inch))
            
            token_table = self._create_token_balances_table(token_balances)
            elements.append(token_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Total Account Value
        total_value = self._create_total_value_table(
            balance, crypto_symbol, prices, token_balances
        )
        elements.append(total_value)
        elements.append(Spacer(1, 0.3*inch))
        
        # Token Filter Info
        token_info = self._create_token_info_section(transactions)
        elements.append(token_info)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary Statistics
        summary = self._create_summary_table(transactions, crypto_symbol, prices)
        elements.append(summary)
        elements.append(Spacer(1, 0.3*inch))
        
        # Transaction History
        if transactions:
            tx_heading = Paragraph("Transaction History", self.styles['CustomHeading'])
            elements.append(tx_heading)
            elements.append(Spacer(1, 0.1*inch))
            
            tx_table = self._create_transaction_table(transactions, crypto_symbol, prices)
            elements.append(tx_table)
        else:
            no_tx = Paragraph("No transactions found in the selected date range.", self.styles['CustomBody'])
            elements.append(no_tx)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
            f"Exchange Rates: 1 USD = 3.67 AED",
            self.styles['CustomBody']
        )
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _create_account_info_table(
        self, address: str, blockchain: str, balance: float,
        crypto_symbol: str, prices: Dict, date_range: Dict
    ) -> Table:
        """Create account information table"""
        balance_usd = balance * prices['usd']
        balance_aed = balance * prices['aed']
        
        data = [
            ['ACCOUNT DETAILS', ''],
            ['Blockchain', blockchain.upper()],
            ['Wallet Address', f"{address[:10]}...{address[-8:]}"],
            ['Statement Period', f"{date_range['start']} to {date_range['end']}"],
            ['', ''],
            [f'{crypto_symbol} BALANCE', ''],
            [f'Amount', f"{balance:.6f} {crypto_symbol}"],
            ['USD Value', f"${balance_usd:,.2f}"],
            ['AED Value', f"AED {balance_aed:,.2f}"],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, 4), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 6), (0, 8), 'Helvetica-Bold'),
            ('ALIGN', (1, 6), (1, 8), 'RIGHT'),
        ]))
        
        return table
    
    def _create_token_balances_table(self, token_balances: Dict[str, Dict]) -> Table:
        """Create token balances table"""
        data = [
            ['Token', 'Balance', 'USD Value', 'AED Value']
        ]
        
        # Sort tokens by USD value (highest first)
        sorted_tokens = sorted(
            token_balances.items(),
            key=lambda x: x[1]['value_usd'],
            reverse=True
        )
        
        for token_symbol, token_info in sorted_tokens:
            data.append([
                f"{token_symbol}",
                f"{token_info['balance']:.6f}",
                f"${token_info['value_usd']:,.2f}",
                f"AED {token_info['value_aed']:,.2f}"
            ])
        
        table = Table(data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        return table
    
    def _create_total_value_table(
        self, balance: float, crypto_symbol: str, prices: Dict,
        token_balances: Dict[str, Dict] = None
    ) -> Table:
        """Create total account value table"""
        # Calculate native token value
        native_value_usd = balance * prices['usd']
        native_value_aed = balance * prices['aed']
        
        # Calculate token values
        token_value_usd = 0
        token_value_aed = 0
        if token_balances:
            for token_info in token_balances.values():
                token_value_usd += token_info['value_usd']
                token_value_aed += token_info['value_aed']
        
        # Calculate totals
        total_value_usd = native_value_usd + token_value_usd
        total_value_aed = native_value_aed + token_value_aed
        
        data = [
            ['TOTAL ACCOUNT VALUE', '', ''],
            ['Asset Type', 'USD Value', 'AED Value'],
            [f'{crypto_symbol} Balance', f'${native_value_usd:,.2f}', f'AED {native_value_aed:,.2f}'],
        ]
        
        if token_balances:
            data.append(['Token Holdings', f'${token_value_usd:,.2f}', f'AED {token_value_aed:,.2f}'])
        
        data.append(['', '', ''])
        data.append(['GRAND TOTAL', f'${total_value_usd:,.2f}', f'AED {total_value_aed:,.2f}'])
        
        table = Table(data, colWidths=[2.5*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 2), (-1, 3 if token_balances else 2), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
        ]))
        
        return table
    
    def _create_token_info_section(self, transactions: List[Dict]) -> Paragraph:
        """Create information about included tokens"""
        # Get unique tokens from transactions
        token_transfers = [tx for tx in transactions if tx.get('type') == 'Token Transfer']
        unique_tokens = set()
        for tx in token_transfers:
            token_symbol = tx.get('tokenSymbol', tx.get('token', 'Unknown'))
            if token_symbol != 'Unknown':
                unique_tokens.add(token_symbol)
        
        if unique_tokens:
            tokens_list = ', '.join(sorted(unique_tokens))
            info_text = (
                f"<b>Included Tokens:</b> {tokens_list}<br/>"
                f"<i>Note: Only whitelisted tokens are included to filter out spam/dusting attacks. "
                f"Native transactions (ETH, MATIC, BNB, etc.) are always included.</i>"
            )
        else:
            info_text = (
                f"<i>Note: Only whitelisted tokens are included to filter out spam/dusting attacks. "
                f"This statement contains native transactions only.</i>"
            )
        
        return Paragraph(info_text, self.styles['CustomBody'])
    
    def _create_summary_table(
        self, transactions: List[Dict], crypto_symbol: str, prices: Dict
    ) -> Table:
        """Create summary statistics table"""
        # Debug: Check transaction amounts
        if transactions:
            print(f"DEBUG: First transaction amount: {transactions[0].get('amount', 'N/A')}")
            print(f"DEBUG: Total transactions: {len(transactions)}")
        
        total_in = sum(tx['amount'] for tx in transactions if tx['direction'] == 'in')
        total_out = sum(tx['amount'] for tx in transactions if tx['direction'] == 'out')
        net_change = total_in - total_out
        
        print(f"DEBUG: Total in: {total_in}, Total out: {total_out}, Net: {net_change}")
        
        total_in_usd = total_in * prices['usd']
        total_in_aed = total_in * prices['aed']
        total_out_usd = total_out * prices['usd']
        total_out_aed = total_out * prices['aed']
        net_change_usd = net_change * prices['usd']
        net_change_aed = net_change * prices['aed']
        
        data = [
            ['Summary Statistics', '', '', ''],
            ['', crypto_symbol, 'USD', 'AED'],
            ['Total Received', f'{total_in:.6f}', f'${total_in_usd:,.2f}', f'AED {total_in_aed:,.2f}'],
            ['Total Sent', f'{total_out:.6f}', f'${total_out_usd:,.2f}', f'AED {total_out_aed:,.2f}'],
            ['Net Change', f'{net_change:.6f}', f'${net_change_usd:,.2f}', f'AED {net_change_aed:,.2f}'],
            ['Total Transactions', str(len(transactions)), '', ''],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
        ]))
        
        return table
    
    def _create_transaction_table(
        self, transactions: List[Dict], crypto_symbol: str, prices: Dict
    ) -> Table:
        """Create transaction history table - includes ALL transactions"""
        data = [
            ['Date', 'Type', 'Amount', 'USD Value', 'AED Value', 'From/To']
        ]
        
        # Include ALL transactions (no limit)
        for tx in transactions:
            date = datetime.fromisoformat(tx['date'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
            tx_type = f"{tx['direction'].upper()} - {tx['type']}"
            amount = tx['amount']
            usd_value = amount * prices['usd']
            aed_value = amount * prices['aed']
            
            # Determine from/to address
            if tx['direction'] == 'in':
                addr = tx.get('from', 'Unknown')
            else:
                addr = tx.get('to', 'Unknown')
            
            addr_short = f"{addr[:6]}...{addr[-4:]}" if len(addr) > 10 else addr
            
            data.append([
                date,
                tx_type,
                f"{amount:.6f} {crypto_symbol}",
                f"${usd_value:,.2f}",
                f"AED {aed_value:,.2f}",
                addr_short
            ])
        
        table = Table(data, colWidths=[1.3*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table
