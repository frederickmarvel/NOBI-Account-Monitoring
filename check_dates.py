"""
Check what date ranges exist in the database
"""

import sys
sys.path.append('/Users/frederickmarvel/Blockchain Monitoring/backend')

from database_service import DatabaseService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database credentials
DB_CONFIG = {
    'host': '217.216.110.33',
    'port': 3306,
    'username': 'root',
    'password': 'nobicuan888',
    'database': 'nobi_wallet_tracker'
}

def check_date_ranges():
    """Check date ranges in database"""
    
    logger.info("="*80)
    logger.info("📅 CHECKING DATE RANGES IN DATABASE")
    logger.info("="*80)
    
    db = DatabaseService(**DB_CONFIG)
    
    if not db.connect():
        logger.error("Failed to connect to database")
        return
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        # Check overall date range
        query = """
        SELECT 
            MIN(timestamp) as earliest,
            MAX(timestamp) as latest,
            COUNT(*) as total_count
        FROM transaction_history
        WHERE value IS NOT NULL
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        logger.info(f"\n📊 Overall Transaction Data:")
        logger.info(f"   Earliest: {result['earliest']}")
        logger.info(f"   Latest: {result['latest']}")
        logger.info(f"   Total with value: {result['total_count']:,}")
        
        # Check for NOBI LABS LEDGER
        eth_address = "0x455e53cbb86018ac2b8092fdcd39d8444affc3f6"
        
        query = """
        SELECT 
            MIN(timestamp) as earliest,
            MAX(timestamp) as latest,
            COUNT(*) as total_count,
            COUNT(DISTINCT asset) as unique_assets
        FROM transaction_history
        WHERE LOWER(walletAddress) = LOWER(%s)
        AND value IS NOT NULL
        """
        
        cursor.execute(query, (eth_address,))
        result = cursor.fetchone()
        
        logger.info(f"\n📊 NOBI LABS LEDGER ({eth_address}):")
        logger.info(f"   Earliest: {result['earliest']}")
        logger.info(f"   Latest: {result['latest']}")
        logger.info(f"   Total transactions: {result['total_count']:,}")
        logger.info(f"   Unique assets: {result['unique_assets']}")
        
        # Show some sample transactions
        query = """
        SELECT 
            timestamp,
            asset,
            value,
            direction,
            network
        FROM transaction_history
        WHERE LOWER(walletAddress) = LOWER(%s)
        AND value IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 10
        """
        
        cursor.execute(query, (eth_address,))
        transactions = cursor.fetchall()
        
        logger.info(f"\n📋 Last 10 transactions for NOBI LABS LEDGER:")
        for i, tx in enumerate(transactions, 1):
            logger.info(f"\n   {i}. {tx['timestamp']}")
            logger.info(f"      {tx['direction']}: {tx['value']} {tx['asset']}")
            logger.info(f"      Network: {tx['network']}")
        
        # Check Solana wallet
        sol_address = "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc"
        
        query = """
        SELECT 
            MIN(timestamp) as earliest,
            MAX(timestamp) as latest,
            COUNT(*) as total_count,
            COUNT(DISTINCT asset) as unique_assets
        FROM transaction_history
        WHERE walletAddress = %s
        AND value IS NOT NULL
        """
        
        cursor.execute(query, (sol_address,))
        result = cursor.fetchone()
        
        logger.info(f"\n\n📊 SQUADS LABS TREASURY ({sol_address}):")
        logger.info(f"   Earliest: {result['earliest']}")
        logger.info(f"   Latest: {result['latest']}")
        logger.info(f"   Total transactions: {result['total_count']:,}")
        logger.info(f"   Unique assets: {result['unique_assets']}")
        
        # Show sample transactions
        query = """
        SELECT 
            timestamp,
            asset,
            value,
            direction,
            network
        FROM transaction_history
        WHERE walletAddress = %s
        AND value IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 10
        """
        
        cursor.execute(query, (sol_address,))
        transactions = cursor.fetchall()
        
        logger.info(f"\n📋 Last 10 transactions for SQUADS LABS TREASURY:")
        for i, tx in enumerate(transactions, 1):
            logger.info(f"\n   {i}. {tx['timestamp']}")
            logger.info(f"      {tx['direction']}: {tx['value']} {tx['asset']}")
            logger.info(f"      Network: {tx['network']}")
        
        cursor.close()
        
    finally:
        db.disconnect()
    
    logger.info("\n" + "="*80)
    logger.info("✅ COMPLETE")
    logger.info("="*80)

if __name__ == '__main__':
    check_date_ranges()
