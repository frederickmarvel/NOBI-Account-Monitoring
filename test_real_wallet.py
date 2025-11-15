"""
Test opening balance with actual wallet data
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

def test_with_real_wallet():
    """Test with wallet that has data"""
    
    logger.info("="*80)
    logger.info("💰 TESTING WITH REAL WALLET DATA")
    logger.info("="*80)
    
    db = DatabaseService(**DB_CONFIG)
    
    if not db.connect():
        logger.error("Failed to connect to database")
        return
    
    try:
        # Use the Solana wallet that has data from July 2024 to Sep 2025
        wallet_address = "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc"
        
        # Test Case 1: Opening balance before any transactions
        logger.info(f"\n{'='*80}")
        logger.info("TEST 1: Opening Balance BEFORE any transactions (Jan 1, 2024)")
        logger.info(f"{'='*80}")
        
        opening1 = db.calculate_opening_balance(wallet_address, "2024-01-01", network='sol-mainnet')
        logger.info(f"\n📊 Result:")
        logger.info(f"   Transactions counted: {opening1['transactions_counted']}")
        logger.info(f"   Balances: {opening1['balances']}")
        logger.info(f"   Expected: 0 transactions, empty balances")
        
        # Test Case 2: Opening balance after first transaction (August 1, 2024)
        logger.info(f"\n{'='*80}")
        logger.info("TEST 2: Opening Balance as of August 1, 2024 (after first transactions)")
        logger.info(f"{'='*80}")
        
        opening2 = db.calculate_opening_balance(wallet_address, "2024-08-01", network='sol-mainnet')
        logger.info(f"\n📊 Result:")
        logger.info(f"   Transactions counted: {opening2['transactions_counted']}")
        logger.info(f"   Balances:")
        for token, balance in sorted(opening2['balances'].items()):
            logger.info(f"      {token}: {balance:,.6f}")
        
        # Test Case 3: Opening balance as of March 29, 2025 (mid-period)
        logger.info(f"\n{'='*80}")
        logger.info("TEST 3: Opening Balance as of March 29, 2025")
        logger.info(f"{'='*80}")
        
        opening3 = db.calculate_opening_balance(wallet_address, "2025-03-29", network='sol-mainnet')
        logger.info(f"\n📊 Result:")
        logger.info(f"   Transactions counted: {opening3['transactions_counted']}")
        logger.info(f"   Balances:")
        for token, balance in sorted(opening3['balances'].items()):
            logger.info(f"      {token}: {balance:,.6f}")
        
        # Test Case 4: Current balance (all transactions)
        logger.info(f"\n{'='*80}")
        logger.info("TEST 4: Current Balance (as of today)")
        logger.info(f"{'='*80}")
        
        current = db.get_current_balance(wallet_address, network='sol-mainnet')
        logger.info(f"\n📊 Result:")
        logger.info(f"   Balances:")
        for token, balance in sorted(current['balances'].items()):
            logger.info(f"      {token}: {balance:,.6f}")
        
        # Test Case 5: Transactions in period
        logger.info(f"\n{'='*80}")
        logger.info("TEST 5: Transactions from July 1, 2024 to August 31, 2024")
        logger.info(f"{'='*80}")
        
        transactions = db.get_transactions_in_period(
            wallet_address, 
            "2024-07-01", 
            "2024-08-31", 
            network='sol-mainnet'
        )
        
        logger.info(f"\n📋 Found {len(transactions)} transactions")
        for i, tx in enumerate(transactions, 1):
            logger.info(f"\n   {i}. {tx['transaction_date']}")
            logger.info(f"      {tx['direction']}: {tx['amount']} {tx['token_symbol']}")
            logger.info(f"      Hash: {tx['transaction_hash'][:16]}...")
        
        # Test with HNST wallet
        logger.info(f"\n\n{'='*80}")
        logger.info("TEST 6: HNST Liquidity Wallet (2 transactions in March 2025)")
        logger.info(f"{'='*80}")
        
        hnst_wallet = "8vCyN7KQ2EZ6NbnUs8tYTYbUfJLiZp7rdqFRLj9PNtVg"
        
        hnst_opening = db.calculate_opening_balance(hnst_wallet, "2025-03-30", network='sol-mainnet')
        logger.info(f"\n📊 Opening Balance as of March 30, 2025:")
        logger.info(f"   Transactions counted: {hnst_opening['transactions_counted']}")
        logger.info(f"   Balances:")
        for token, balance in sorted(hnst_opening['balances'].items()):
            logger.info(f"      {token}: {balance:,.6f}")
        
        hnst_current = db.get_current_balance(hnst_wallet, network='sol-mainnet')
        logger.info(f"\n📊 Current Balance:")
        for token, balance in sorted(hnst_current['balances'].items()):
            logger.info(f"      {token}: {balance:,.6f}")
        
    finally:
        db.disconnect()
    
    logger.info("\n" + "="*80)
    logger.info("✅ ALL TESTS COMPLETE")
    logger.info("="*80)

if __name__ == '__main__':
    test_with_real_wallet()
