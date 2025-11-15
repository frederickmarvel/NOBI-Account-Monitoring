"""
Test Opening Balance Calculation
Example: Calculate opening balance as of March 31, 2025
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

def test_opening_balance():
    """Test opening balance calculation"""
    
    logger.info("="*80)
    logger.info("💰 TESTING OPENING BALANCE CALCULATION")
    logger.info("="*80)
    
    # Create database service
    db = DatabaseService(**DB_CONFIG)
    
    # Connect
    if not db.connect():
        logger.error("Failed to connect to database")
        return
    
    try:
        # Test wallet address (NOBI LABS LEDGER)
        wallet_address = "0x455e53cbb86018ac2b8092fdcd39d8444affc3f6"
        cutoff_date = "2025-03-31"
        end_date = "2025-11-15"
        
        logger.info(f"\n📍 Wallet: {wallet_address}")
        logger.info(f"📅 Opening Balance Date: {cutoff_date}")
        logger.info(f"📅 Current Balance Date: {end_date}")
        
        # Calculate opening balance
        logger.info(f"\n{'='*80}")
        logger.info("1️⃣  CALCULATING OPENING BALANCE (as of March 31, 2025)")
        logger.info(f"{'='*80}")
        
        opening = db.calculate_opening_balance(wallet_address, cutoff_date)
        
        logger.info(f"\n📊 Opening Balance Summary:")
        logger.info(f"   Date: {opening['opening_date']}")
        logger.info(f"   Transactions counted: {opening['transactions_counted']}")
        logger.info(f"   Tokens found: {len(opening['balances'])}")
        logger.info(f"\n   Balances:")
        for token, balance in sorted(opening['balances'].items()):
            if balance > 0:
                logger.info(f"      {token}: {balance:,.6f}")
        
        # Calculate current balance
        logger.info(f"\n{'='*80}")
        logger.info("2️⃣  CALCULATING CURRENT BALANCE (as of November 15, 2025)")
        logger.info(f"{'='*80}")
        
        current = db.get_current_balance(wallet_address, end_date)
        
        logger.info(f"\n📊 Current Balance Summary:")
        logger.info(f"   Date: {current['current_date']}")
        logger.info(f"   Tokens found: {len(current['balances'])}")
        logger.info(f"\n   Balances:")
        for token, balance in sorted(current['balances'].items()):
            if balance > 0:
                logger.info(f"      {token}: {balance:,.6f}")
        
        # Get transactions in period
        logger.info(f"\n{'='*80}")
        logger.info(f"3️⃣  TRANSACTIONS FROM {cutoff_date} TO {end_date}")
        logger.info(f"{'='*80}")
        
        transactions = db.get_transactions_in_period(wallet_address, cutoff_date, end_date)
        
        logger.info(f"\n📋 Found {len(transactions)} transactions in period")
        logger.info(f"\n   First 5 transactions:")
        for i, tx in enumerate(transactions[:5], 1):
            logger.info(f"\n   Transaction {i}:")
            logger.info(f"      Date: {tx['transaction_date']}")
            logger.info(f"      Type: {tx['transaction_type']}")
            logger.info(f"      Asset: {tx['token_symbol']}")
            logger.info(f"      Direction: {tx['direction']}")
            logger.info(f"      Amount: {tx['amount']}")
            logger.info(f"      Network: {tx['network']}")
        
        # Test with Solana wallet
        logger.info(f"\n\n{'='*80}")
        logger.info("4️⃣  TESTING WITH SOLANA WALLET")
        logger.info(f"{'='*80}")
        
        sol_address = "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc"
        sol_cutoff = "2025-04-01"
        
        logger.info(f"\n📍 Wallet: {sol_address}")
        logger.info(f"📅 Opening Balance Date: {sol_cutoff}")
        
        sol_opening = db.calculate_opening_balance(sol_address, sol_cutoff, network='sol-mainnet')
        
        logger.info(f"\n📊 Solana Opening Balance:")
        logger.info(f"   Transactions counted: {sol_opening['transactions_counted']}")
        if sol_opening['balances']:
            for token, balance in sorted(sol_opening['balances'].items()):
                if balance > 0:
                    logger.info(f"      {token}: {balance:,.6f}")
        else:
            logger.info("   No balances found (or all transactions after cutoff date)")
        
    finally:
        db.disconnect()
    
    logger.info("\n" + "="*80)
    logger.info("✅ TEST COMPLETE")
    logger.info("="*80)

if __name__ == '__main__':
    test_opening_balance()
