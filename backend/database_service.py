"""
Database Service for Blockchain Transaction History
Connects to MySQL database and calculates opening balances
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                logger.info(f"✅ Connected to MySQL database: {self.database}")
                return True
        except Error as e:
            logger.error(f"❌ Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("🔌 Database connection closed")
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            return tables
        except Error as e:
            logger.error(f"Error getting tables: {e}")
            return []
    
    def get_table_structure(self, table_name: str) -> List[Dict]:
        """Get structure of a specific table"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'field': row[0],
                    'type': row[1],
                    'null': row[2],
                    'key': row[3],
                    'default': row[4],
                    'extra': row[5]
                })
            cursor.close()
            return columns
        except Error as e:
            logger.error(f"Error getting table structure: {e}")
            return []
    
    def get_transaction_history(self, address: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get transaction history for a specific address
        
        Args:
            address: Wallet address
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
        
        Returns:
            List of transaction records
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Build query
            query = """
                SELECT * FROM transactions 
                WHERE wallet_address = %s
            """
            params = [address]
            
            if start_date:
                query += " AND transaction_date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND transaction_date <= %s"
                params.append(end_date)
            
            query += " ORDER BY transaction_date ASC"
            
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            cursor.close()
            
            logger.info(f"📊 Found {len(transactions)} transactions for {address}")
            return transactions
            
        except Error as e:
            logger.error(f"Error getting transaction history: {e}")
            return []
    
    def get_wallet_id(self, wallet_address):
        """
        Get wallet ID from address (handles case-insensitive lookup)
        
        Args:
            wallet_address: Wallet address to look up
            
        Returns:
            str: Wallet ID (UUID) or None if not found
        """
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Query wallets table with case-insensitive address match
            query = "SELECT id FROM wallets WHERE LOWER(address) = LOWER(%s)"
            cursor.execute(query, (wallet_address,))
            result = cursor.fetchone()
            
            # Important: Consume any remaining results before closing cursor
            try:
                cursor.fetchall()
            except:
                pass
            
            cursor.close()
            
            if result:
                return result['id']
            return None
            
        except Exception as e:
            self.logger.error(f"Error looking up wallet ID: {str(e)}")
            return None
    
    def calculate_opening_balance(self, wallet_address, cutoff_date, network=None):
        """
        Calculate opening balance as of a specific cutoff date
        
        Args:
            wallet_address: Wallet address to calculate balance for
            cutoff_date: Date string (YYYY-MM-DD) - calculate balance BEFORE this date
            network: Optional network filter (e.g., 'eth-mainnet', 'sol-mainnet')
            
        Returns:
            dict: {
                'opening_date': cutoff_date,
                'balances': {'ETH': 10.5, 'USDC': 1000.0, ...},
                'transactions_counted': 15
            }
        """
        if not self.connection:
            self.logger.error("Not connected to database")
            return {'opening_date': cutoff_date, 'balances': {}, 'transactions_counted': 0}
        
        try:
            # Get wallet ID from address
            wallet_id = self.get_wallet_id(wallet_address)
            if not wallet_id:
                self.logger.warning(f"Wallet not found: {wallet_address}")
                return {'opening_date': cutoff_date, 'balances': {}, 'transactions_counted': 0}
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Query transactions BEFORE the cutoff date with non-null values
            # Use walletId since walletAddress may be empty for EVM chains
            query = """
                SELECT asset, value, direction
                FROM transaction_history
                WHERE walletId = %s
                AND timestamp < %s
                AND value IS NOT NULL
                AND asset IS NOT NULL
            """
            
            params = [wallet_id, f"{cutoff_date} 23:59:59"]
            
            # Add network filter if provided
            if network:
                query += " AND network = %s"
                params.append(network)
            
            query += " ORDER BY timestamp ASC"
            
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            
            # Calculate balance per token
            balances = {}
            for tx in transactions:
                token = tx['asset']
                value = float(tx['value'])
                direction = tx['direction']
                
                if token not in balances:
                    balances[token] = 0.0
                
                # Add for incoming, subtract for outgoing
                if direction == 'incoming':
                    balances[token] += value
                else:  # outgoing
                    balances[token] -= value
            
            cursor.close()
            
            self.logger.info(f"💰 Opening balance as of {cutoff_date}: {len(balances)} tokens, {len(transactions)} transactions")
            for token, balance in balances.items():
                if balance > 0:
                    self.logger.info(f"   {token}: {balance}")
            
            return {
                'opening_date': cutoff_date,
                'balances': balances,
                'transactions_counted': len(transactions)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating opening balance: {str(e)}")
            return {'opening_date': cutoff_date, 'balances': {}, 'transactions_counted': 0}
    
    def get_current_balance(self, wallet_address, end_date=None, network=None):
        """
        Calculate current balance up to a specific end date
        
        Args:
            wallet_address: Wallet address to calculate balance for
            end_date: Optional date string (YYYY-MM-DD) - calculate balance up to this date
                     If None, uses current datetime
            network: Optional network filter (e.g., 'eth-mainnet', 'sol-mainnet')
            
        Returns:
            dict: {
                'current_date': end_date or current datetime,
                'balances': {'ETH': 15.2, 'USDC': 1200.0, ...}
            }
        """
        if not self.connection:
            self.logger.error("Not connected to database")
            return {'current_date': end_date, 'balances': {}}
        
        try:
            # Get wallet ID from address
            wallet_id = self.get_wallet_id(wallet_address)
            if not wallet_id:
                self.logger.warning(f"Wallet not found: {wallet_address}")
                return {'current_date': end_date, 'balances': {}}
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Query all transactions up to end_date with non-null values
            query = """
                SELECT asset, value, direction
                FROM transaction_history
                WHERE walletId = %s
                AND value IS NOT NULL
                AND asset IS NOT NULL
            """
            
            params = [wallet_id]
            
            # Add date filter if provided
            if end_date:
                query += " AND timestamp <= %s"
                params.append(f"{end_date} 23:59:59")
            
            # Add network filter if provided
            if network:
                query += " AND network = %s"
                params.append(network)
            
            query += " ORDER BY timestamp ASC"
            
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            
            # Calculate balance per token
            balances = {}
            for tx in transactions:
                token = tx['asset']
                value = float(tx['value'])
                direction = tx['direction']
                
                if token not in balances:
                    balances[token] = 0.0
                
                # Add for incoming, subtract for outgoing
                if direction == 'incoming':
                    balances[token] += value
                else:  # outgoing
                    balances[token] -= value
            
            cursor.close()
            
            self.logger.info(f"📊 Current balance as of {end_date or 'now'}: {len(balances)} tokens")
            
            return {
                'current_date': end_date or datetime.now().strftime('%Y-%m-%d'),
                'balances': balances
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating current balance: {str(e)}")
            return {'current_date': end_date, 'balances': {}}
    
    def get_transactions_in_period(self, wallet_address, start_date, end_date, network=None):
        """
        Get all transactions in a specific period for display
        
        Args:
            wallet_address: Wallet address to get transactions for
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            network: Optional network filter
            
        Returns:
            list: List of transaction dicts with formatted data for frontend display
        """
        if not self.connection:
            self.logger.error("Not connected to database")
            return []
        
        try:
            # Get wallet ID from address
            wallet_id = self.get_wallet_id(wallet_address)
            if not wallet_id:
                self.logger.warning(f"Wallet not found: {wallet_address}")
                return []
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Query transactions in the period
            query = """
                SELECT 
                    hash as transaction_hash,
                    timestamp as transaction_date,
                    asset as token_symbol,
                    value as amount,
                    direction,
                    usdValue as usd_value,
                    network,
                    fromAddress as from_address,
                    toAddress as to_address,
                    category as transaction_type
                FROM transaction_history
                WHERE walletId = %s
                AND timestamp >= %s
                AND timestamp <= %s
            """
            
            params = [wallet_id, f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
            
            # Add network filter if provided
            if network:
                query += " AND network = %s"
                params.append(network)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            
            cursor.close()
            
            self.logger.info(f"📋 Found {len(transactions)} transactions between {start_date} and {end_date}")
            
            return transactions
            
        except Exception as e:
            self.logger.error(f"Error getting transactions: {str(e)}")
            return []
