#!/bin/bash

echo "=================================="
echo "API TRANSACTION HISTORY TEST"
echo "=================================="
echo ""

# Wait for backend
sleep 2

# Test ETH
echo "📊 TESTING ETHEREUM TRANSACTIONS"
echo "=================================="
curl -s "http://localhost:8085/api/analyze/ethereum/0x742d35Cc6634C0532925a3b844Bc454e4438f44e?start_date=2024-01-01&end_date=2025-11-04" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('SUCCESS: ', data.get('success', False))
    print('Balance:', data.get('balance', 'N/A'))
    print('Transaction Count:', data.get('count', 0))
    print('')
    print('FIRST 3 TRANSACTIONS:')
    print('-' * 80)
    for i, tx in enumerate(data.get('transactions', [])[:3]):
        print(f'\nTransaction {i+1}:')
        print(f'  Hash: {tx.get(\"hash\", \"N/A\")}')
        print(f'  Type: {tx.get(\"type\", \"N/A\")}')
        print(f'  Direction: {tx.get(\"direction\", \"N/A\")}')
        print(f'  From: {tx.get(\"from\", \"N/A\")[:50]}...')
        print(f'  To: {tx.get(\"to\", \"N/A\")[:50]}...')
        print(f'  Amount: {tx.get(\"amount\", 0)}')
        print(f'  Token: {tx.get(\"tokenSymbol\", \"ETH\")}')
        print(f'  Status: {tx.get(\"status\", \"N/A\")}')
except Exception as e:
    print(f'ERROR: {e}')
"

echo ""
echo ""
echo "📊 TESTING SOLANA TRANSACTIONS"
echo "=================================="
curl -s "http://localhost:8085/api/analyze/solana/9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc?start_date=2025-04-01&end_date=2025-11-04" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('SUCCESS: ', data.get('success', False))
    print('Balance:', data.get('balance', 'N/A'))
    print('Transaction Count:', data.get('count', 0))
    print('')
    print('FIRST 3 TRANSACTIONS:')
    print('-' * 80)
    for i, tx in enumerate(data.get('transactions', [])[:3]):
        print(f'\nTransaction {i+1}:')
        print(f'  Hash: {tx.get(\"hash\", \"N/A\")}')
        print(f'  Type: {tx.get(\"type\", \"N/A\")}')
        print(f'  Direction: {tx.get(\"direction\", \"N/A\")}')
        print(f'  From: {tx.get(\"from\", \"N/A\")[:50]}...')
        print(f'  To: {tx.get(\"to\", \"N/A\")[:50]}...')
        print(f'  Amount: {tx.get(\"amount\", 0)}')
        print(f'  Token: {tx.get(\"tokenSymbol\", \"SOL\")}')
        print(f'  Status: {tx.get(\"status\", \"N/A\")}')
except Exception as e:
    print(f'ERROR: {e}')
"

echo ""
echo "=================================="
echo "✅ TEST COMPLETE"
echo "=================================="
