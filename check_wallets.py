"""
Check what wallet addresses actually have transactions
"""

import sys
sys.path.append('/Users/frederickmarvel/Blockchain Monitoring/backend')

from database_service import DatabaseService
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': '217.216.110.33',
    'port': 3306,
    'username': 'root',
    'password': 'nobicuan888',
    'database': 'nobi_wallet_tracker'
}

def check_wallets():
    """Check what wallets have transactions"""
    
    logger.info("="*80)
    logger.info("👛 CHECKING WALLET ADDRESSES WITH TRANSACTIONS")
    logger.info("="*80)
    
    db = DatabaseService(**DB_CONFIG)
    
    if not db.connect():
        logger.error("Failed to connect to database")
        return
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        # Get all unique wallet addresses with transaction counts
        query = """
        SELECT 
            walletAddress,
            COUNT(*) as total_transactions,
            COUNT(CASE WHEN value IS NOT NULL THEN 1 END) as transactions_with_value,
            MIN(timestamp) as earliest,
            MAX(timestamp) as latest,
            network
        FROM transaction_history
        GROUP BY walletAddress, network
        HAVING COUNT(*) > 0
        ORDER BY transactions_with_value DESC
        """
        
        cursor.execute(query)
        wallets = cursor.fetchall()
        
        logger.info(f"\n📊 Found {len(wallets)} wallet-network combinations with transactions:\n")
        
        for i, wallet in enumerate(wallets, 1):
            logger.info(f"{i}. Wallet: {wallet['walletAddress']}")
            logger.info(f"   Network: {wallet['network']}")
            logger.info(f"   Total transactions: {wallet['total_transactions']:,}")
            logger.info(f"   With value: {wallet['transactions_with_value']:,}")
            logger.info(f"   Date range: {wallet['earliest']} to {wallet['latest']}")
            
            # Get sample transactions for this wallet
            sample_query = """
            SELECT timestamp, asset, value, direction
            FROM transaction_history
            WHERE walletAddress = %s AND network = %s AND value IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 3
            """
            
            cursor.execute(sample_query, (wallet['walletAddress'], wallet['network']))
            samples = cursor.fetchall()
            
            if samples:
                logger.info(f"   Recent transactions:")
                for sample in samples:
                    logger.info(f"      {sample['timestamp']}: {sample['direction']} {sample['value']} {sample['asset']}")
            
            logger.info("")
        
        cursor.close()
        
    finally:
        db.disconnect()
    
    logger.info("="*80)
    logger.info("✅ COMPLETE")
    logger.info("="*80)

if __name__ == '__main__':
    check_wallets()
