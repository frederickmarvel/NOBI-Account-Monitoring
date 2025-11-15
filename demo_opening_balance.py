#!/usr/bin/env python3
"""
OPENING BALANCE CALCULATION DEMONSTRATION

This demonstrates the core concept:
- Opening Balance = Sum of all transactions BEFORE the cutoff date
- Example: Opening balance on March 31, 2025 = all movements before March 31
"""

import sys
sys.path.append('backend')
from database_service import DatabaseService
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Database connection
db = DatabaseService(
    host='217.216.110.33',
    port=3306,
    username='root',
    password='nobicuan888',
    database='nobi_wallet_tracker'
)

def print_separator(title):
    """Print a nice separator"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def demonstrate_opening_balance():
    """Demonstrate opening balance calculation with clear examples"""
    
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        print_separator("💰 OPENING BALANCE CALCULATION DEMO")
        
        # Example 1: Solana SQUADS LABS TREASURY
        wallet1 = "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc"
        
        print("📍 Wallet: SQUADS LABS TREASURY (Solana)")
        print(f"   Address: {wallet1}\n")
        
        # Scenario 1: Opening balance on March 1, 2025
        print("SCENARIO 1: What was my opening balance on March 1, 2025?")
        print("   → This means: Calculate all transactions BEFORE March 1, 2025\n")
        
        opening_march = db.calculate_opening_balance(wallet1, "2025-03-01", network="sol-mainnet")
        
        print(f"   ✅ Opening Balance as of March 1, 2025:")
        print(f"      Transactions counted: {opening_march['transactions_counted']}")
        if opening_march['balances']:
            for token, balance in sorted(opening_march['balances'].items()):
                print(f"      {token}: {balance:,.6f}")
        else:
            print("      No transactions before this date")
        
        # Scenario 2: Opening balance on April 1, 2025
        print("\n" + "-"*80)
        print("\nSCENARIO 2: What was my opening balance on April 1, 2025?")
        print("   → This means: Calculate all transactions BEFORE April 1, 2025\n")
        
        opening_april = db.calculate_opening_balance(wallet1, "2025-04-01", network="sol-mainnet")
        
        print(f"   ✅ Opening Balance as of April 1, 2025:")
        print(f"      Transactions counted: {opening_april['transactions_counted']}")
        if opening_april['balances']:
            for token, balance in sorted(opening_april['balances'].items()):
                print(f"      {token}: {balance:,.6f}")
        
        # Scenario 3: Current balance (all time)
        print("\n" + "-"*80)
        print("\nSCENARIO 3: What is my current balance today?")
        print("   → This means: Calculate ALL transactions up to now\n")
        
        current = db.get_current_balance(wallet1, network="sol-mainnet")
        
        print(f"   ✅ Current Balance (as of {current['current_date']}):")
        if current['balances']:
            for token, balance in sorted(current['balances'].items()):
                print(f"      {token}: {balance:,.6f}")
        
        # Show the logic
        print_separator("📚 HOW IT WORKS")
        print("FORMULA:")
        print("   Opening Balance = Σ(incoming transactions) - Σ(outgoing transactions)")
        print("   WHERE timestamp < cutoff_date AND value IS NOT NULL\n")
        
        print("EXAMPLE CALCULATION:")
        print("   If you had these transactions before March 1, 2025:")
        print("   • July 9, 2024: +0.001 SOL (incoming)")
        print("   • July 9, 2024: +0.001 SOL (incoming)")
        print("   • Total: 0.002 SOL")
        print("\n   Then your opening balance on March 1, 2025 = 0.002 SOL ✅")
        
        # Example 2: Ethereum wallet with more complex data
        print_separator("🔷 ETHEREUM EXAMPLE - NOBI LABS LEDGER")
        
        eth_wallet = "0x455e53cbb86018ac2b8092fdcd39d8444affc3f6"
        
        print("📍 Wallet: NOBI LABS LEDGER (Multi-chain)")
        print(f"   Address: {eth_wallet}\n")
        
        print("SCENARIO: Opening balance on January 1, 2024")
        print("   → Counting all transactions BEFORE Jan 1, 2024\n")
        
        eth_opening = db.calculate_opening_balance(eth_wallet, "2024-01-01")
        
        print(f"   ✅ Opening Balance as of January 1, 2024:")
        print(f"      Transactions counted: {eth_opening['transactions_counted']}")
        print(f"      Unique tokens: {len(eth_opening['balances'])}")
        
        if eth_opening['balances']:
            print(f"\n      Top 10 tokens by balance:")
            sorted_balances = sorted(eth_opening['balances'].items(), key=lambda x: abs(x[1]), reverse=True)
            for token, balance in sorted_balances[:10]:
                if balance != 0:
                    print(f"      {token}: {balance:,.2f}")
        
        # Show date range
        print_separator("📅 PRACTICAL USE CASE")
        print("USER REQUEST: 'Show me my financial statement from March 1 to Oct 1, 2025'\n")
        print("SYSTEM CALCULATION:")
        print("   1️⃣  Opening Balance (March 1): All transactions BEFORE March 1")
        print("   2️⃣  Transactions in Period: Transactions FROM March 1 TO Oct 1")
        print("   3️⃣  Closing Balance (Oct 1): All transactions UP TO Oct 1\n")
        
        start = "2025-03-01"
        end = "2025-10-01"
        
        opening = db.calculate_opening_balance(wallet1, start, network="sol-mainnet")
        closing = db.get_current_balance(wallet1, end, network="sol-mainnet")
        transactions = db.get_transactions_in_period(wallet1, start, end, network="sol-mainnet")
        
        print(f"   📊 RESULTS:")
        print(f"      Opening Balance (March 1): {opening['transactions_counted']} transactions counted")
        for token, balance in opening['balances'].items():
            print(f"         {token}: {balance:,.6f}")
        
        print(f"\n      Transactions in Period: {len(transactions)} transactions")
        
        print(f"\n      Closing Balance (Oct 1):")
        for token, balance in closing['balances'].items():
            print(f"         {token}: {balance:,.6f}")
        
        print_separator("✅ DEMONSTRATION COMPLETE")
        print("KEY POINTS:")
        print("   • Opening balance = historical calculation BEFORE the start date")
        print("   • Uses database transactions, not RPC calls")
        print("   • Accurate for any date range with pre-synced data")
        print("   • Handles incoming (+) and outgoing (-) transactions")
        print("   • Supports multiple tokens and networks\n")
        
    finally:
        db.disconnect()

if __name__ == '__main__':
    demonstrate_opening_balance()
