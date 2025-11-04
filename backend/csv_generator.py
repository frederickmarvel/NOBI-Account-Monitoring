"""
CSV Generator for Blockchain Transactions
Generates simple CSV files with transactions and opening balance
"""

import csv
import io
from typing import List, Dict
from datetime import datetime


class CSVGenerator:
    """Generate CSV reports for blockchain transactions"""
    
    def generate_transaction_csv(
        self,
        address: str,
        blockchain: str,
        transactions: List[Dict],
        opening_balance: float,
        current_balance: float,
        crypto_symbol: str,
        opening_token_balances: Dict[str, Dict] = None,
        current_token_balances: Dict[str, Dict] = None,
        start_date: str = None,
        end_date: str = None
    ) -> str:
        """
        Generate CSV with opening balance and all transactions
        
        Args:
            address: Wallet address
            blockchain: Blockchain name
            transactions: List of transactions
            opening_balance: Balance at start of period
            current_balance: Balance at end of period
            crypto_symbol: Native token symbol (ETH, BTC, SOL, etc.)
            opening_token_balances: Token balances at start
            current_token_balances: Token balances at end
            start_date: Start date
            end_date: End date
            
        Returns:
            CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header section
        writer.writerow(['BLOCKCHAIN ACCOUNT STATEMENT'])
        writer.writerow([''])
        writer.writerow(['Blockchain', blockchain.upper()])
        writer.writerow(['Address', address])
        writer.writerow(['Period', f'{start_date} to {end_date}'])
        writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([''])
        
        # Opening Balance Section
        writer.writerow(['OPENING BALANCE', f'(as of {start_date})'])
        writer.writerow(['Asset', 'Balance'])
        writer.writerow([crypto_symbol, f'{opening_balance:.8f}'])
        
        if opening_token_balances:
            for symbol, token_data in opening_token_balances.items():
                writer.writerow([symbol, f'{token_data["balance"]:.8f}'])
        
        writer.writerow([''])
        
        # Current Balance Section
        writer.writerow(['CURRENT BALANCE', f'(as of {end_date})'])
        writer.writerow(['Asset', 'Balance'])
        writer.writerow([crypto_symbol, f'{current_balance:.8f}'])
        
        if current_token_balances:
            for symbol, token_data in current_token_balances.items():
                writer.writerow([symbol, f'{token_data["balance"]:.8f}'])
        
        writer.writerow([''])
        writer.writerow([''])
        
        # Transaction History
        writer.writerow(['TRANSACTION HISTORY'])
        writer.writerow([
            'Date',
            'Time',
            'Hash',
            'Type',
            'Direction',
            'From',
            'To',
            'Amount',
            'Token',
            'Status',
            'Block',
            'Fee'
        ])
        
        # Sort transactions by timestamp (oldest first for CSV)
        sorted_transactions = sorted(transactions, key=lambda x: x.get('timestamp', 0))
        
        for tx in sorted_transactions:
            timestamp = tx.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                date = dt.strftime('%Y-%m-%d')
                time = dt.strftime('%H:%M:%S')
            else:
                date = 'Unknown'
                time = 'Unknown'
            
            # Get fee
            fee = tx.get('fee', 0)
            if fee == 0:
                # Calculate fee from gas if available
                gas_used = tx.get('gasUsed', 0)
                gas_price = tx.get('gasPrice', 0)
                if gas_used and gas_price:
                    fee = (gas_used * gas_price) / 1e9  # Convert to token units
            
            writer.writerow([
                date,
                time,
                tx.get('hash', 'Unknown'),
                tx.get('type', 'Transfer'),
                tx.get('direction', 'unknown'),
                tx.get('from', 'Unknown')[:42],  # Truncate long addresses
                tx.get('to', 'Unknown')[:42],
                f'{tx.get("amount", 0):.8f}',
                tx.get('tokenSymbol', crypto_symbol),
                tx.get('status', 'Success'),
                tx.get('blockNumber', 0),
                f'{fee:.8f}'
            ])
        
        writer.writerow([''])
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Transactions', len(transactions)])
        
        # Calculate summary stats
        incoming = sum(1 for tx in transactions if tx.get('direction') == 'in')
        outgoing = sum(1 for tx in transactions if tx.get('direction') == 'out')
        
        writer.writerow(['Incoming Transactions', incoming])
        writer.writerow(['Outgoing Transactions', outgoing])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
