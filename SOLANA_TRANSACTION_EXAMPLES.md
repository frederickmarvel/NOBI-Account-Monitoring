loo# Solana Transaction Examples

## Example 1: SOL Transfer (From Your Address)

This is a real transaction from `9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc`:

```json
{
  "result": {
    "blockTime": 1756805763,
    "slot": 364139111,
    "meta": {
      "err": null,
      "fee": 32307,
      "innerInstructions": [
        {
          "index": 3,
          "instructions": [
            {
              "parsed": {
                "info": {
                  "destination": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc",
                  "lamports": 107239738734,
                  "source": "7k2PaLH1p8i14PjVC7cAc2sSsSEm2A6XhoQ7NogK8uAr"
                },
                "type": "transfer"
              },
              "program": "system",
              "programId": "11111111111111111111111111111111"
            }
          ]
        }
      ],
      "preBalances": [248950192, 2416941, 3382560, 107240738735, 5401030044],
      "postBalances": [248817885, 2516941, 3382560, 1000001, 112640768778],
      "preTokenBalances": [],
      "postTokenBalances": []
    },
    "transaction": {
      "message": {
        "accountKeys": [
          {"pubkey": "AtyZbL2x2kihQVM9CkjsmbKBHJgsR9MUSTwKZkgQz9jk", "signer": true, "writable": true},
          {"pubkey": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc", "signer": false, "writable": true}
        ],
        "instructions": [
          {
            "parsed": {
              "info": {
                "destination": "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
                "lamports": 100000,
                "source": "AtyZbL2x2kihQVM9CkjsmbKBHJgsR9MUSTwKZkgQz9jk"
              },
              "type": "transfer"
            },
            "program": "system",
            "programId": "11111111111111111111111111111111"
          }
        ]
      },
      "signatures": ["5MV9H7sPEj4moLdMeqVKzzE4LBrby9TEDrUXhRYAp7i7QGfK7aw4DuNAaw4oNo2inv3cozgLATuKvMxj8mU4dv2c"]
    }
  }
}
```

### Key Parts Explained:

**1. Transaction Identification**
```json
{
  "blockTime": 1756805763,  // Unix timestamp
  "slot": 364139111,        // Solana block slot
  "signatures": ["5MV9H7s..."]  // Transaction hash
}
```

**2. Fee & Status**
```json
{
  "meta": {
    "err": null,      // null = success, object = failed
    "fee": 32307      // Fee in lamports (1 SOL = 1,000,000,000 lamports)
  }
}
```

**3. SOL Transfer Detection (innerInstructions)**
```json
{
  "innerInstructions": [
    {
      "instructions": [
        {
          "parsed": {
            "info": {
              "destination": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc",
              "lamports": 107239738734,  // Amount: 107.239738734 SOL
              "source": "7k2PaLH1p8i14PjVC7cAc2sSsSEm2A6XhoQ7NogK8uAr"
            },
            "type": "transfer"  // System transfer
          },
          "program": "system"
        }
      ]
    }
  ]
}
```

**4. Balance Changes**
```json
{
  "preBalances": [248950192, 2416941, 3382560, 107240738735, 5401030044],
  "postBalances": [248817885, 2516941, 3382560, 1000001, 112640768778]
}
```
Account at index 4 (9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc):
- Before: 5,401,030,044 lamports = 5.401 SOL
- After: 112,640,768,778 lamports = 112.64 SOL
- **Received: +107.24 SOL** ✅

---

## Example 2: SPL Token Transfer (HNST)

```json
{
  "result": {
    "blockTime": 1709251200,
    "meta": {
      "err": null,
      "fee": 5000,
      "innerInstructions": [
        {
          "index": 0,
          "instructions": [
            {
              "parsed": {
                "info": {
                  "authority": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc",
                  "destination": "AbcDef123TokenAccount456",
                  "mint": "HNSTRZJNeey2QoYD5D6T48kw2xYMYhwvGt61Hm5BAhJ",
                  "source": "XyzAbc789TokenAccount123",
                  "tokenAmount": {
                    "amount": "524000000000",
                    "decimals": 6,
                    "uiAmount": 524000.0,
                    "uiAmountString": "524000"
                  }
                },
                "type": "transferChecked"
              },
              "program": "spl-token",
              "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            }
          ]
        }
      ],
      "preTokenBalances": [
        {
          "accountIndex": 2,
          "mint": "HNSTRZJNeey2QoYD5D6T48kw2xYMYhwvGt61Hm5BAhJ",
          "owner": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc",
          "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
          "uiTokenAmount": {
            "amount": "0",
            "decimals": 6,
            "uiAmount": 0.0,
            "uiAmountString": "0"
          }
        }
      ],
      "postTokenBalances": [
        {
          "accountIndex": 2,
          "mint": "HNSTRZJNeey2QoYD5D6T48kw2xYMYhwvGt61Hm5BAhJ",
          "owner": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc",
          "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
          "uiTokenAmount": {
            "amount": "524000000000",
            "decimals": 6,
            "uiAmount": 524000.0,
            "uiAmountString": "524000"
          }
        }
      ]
    },
    "transaction": {
      "message": {
        "accountKeys": [
          {"pubkey": "SenderWallet...", "signer": true, "writable": true},
          {"pubkey": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc", "signer": false, "writable": true}
        ]
      }
    }
  }
}
```

### Token Transfer Detection Methods:

**Method 1: innerInstructions (Most Reliable)**
```json
{
  "innerInstructions": [
    {
      "instructions": [
        {
          "parsed": {
            "type": "transferChecked",  // or "transfer"
            "info": {
              "mint": "HNSTRZJNeey2QoYD5D6T48kw2xYMYhwvGt61Hm5BAhJ",
              "tokenAmount": {
                "uiAmount": 524000.0  // Human-readable amount
              }
            }
          }
        }
      ]
    }
  ]
}
```

**Method 2: preTokenBalances / postTokenBalances (Fallback)**
```python
# Calculate token balance change
pre_amount = preTokenBalances[0]['uiTokenAmount']['uiAmount']  # 0.0
post_amount = postTokenBalances[0]['uiTokenAmount']['uiAmount']  # 524000.0
amount_received = post_amount - pre_amount  # 524000.0 HNST
```

**Method 3: Regular instructions (Sometimes)**
```json
{
  "instructions": [
    {
      "parsed": {
        "type": "transfer",
        "info": {
          "mint": "HNSTRZJNeey2QoYD5D6T48kw2xYMYhwvGt61Hm5BAhJ",
          "amount": "524000000000"
        }
      }
    }
  ]
}
```

---

## Example 3: Token-2022 Transfer (PYUSD)

Token-2022 uses a different program ID but similar structure:

```json
{
  "meta": {
    "innerInstructions": [
      {
        "instructions": [
          {
            "parsed": {
              "info": {
                "authority": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc",
                "mint": "2b1kV6DkPAnxd5ixfnxCpjxmKwqjJayMczFHsfu24GXo",
                "tokenAmount": {
                  "amount": "1000000000",
                  "decimals": 6,
                  "uiAmount": 1000.0,
                  "uiAmountString": "1000"
                }
              },
              "type": "transferChecked"
            },
            "program": "spl-token-2022",
            "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
          }
        ]
      }
    ],
    "postTokenBalances": [
      {
        "mint": "2b1kV6DkPAnxd5ixfnxCpjxmKwqjJayMczFHsfu24GXo",
        "owner": "9qa5DezYLRUjYprWdHHrjoJJzZ1wcjN2TVUL3eh9qwmc",
        "programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
        "uiTokenAmount": {
          "uiAmount": 1000.0
        }
      }
    ]
  }
}
```

---

## How Our Code Parses These

### Step 1: Check innerInstructions
```python
for inner_group in meta.get('innerInstructions', []):
    for instruction in inner_group.get('instructions', []):
        if instruction['parsed']['type'] in ['transfer', 'transferChecked']:
            mint = instruction['parsed']['info']['mint']
            if mint in WHITELISTED_TOKENS:
                # Found token transfer!
                amount = instruction['parsed']['info']['tokenAmount']['uiAmount']
```

### Step 2: Fallback to Token Balance Changes
```python
pre_token_balances = meta.get('preTokenBalances', [])
post_token_balances = meta.get('postTokenBalances', [])

for post_bal in post_token_balances:
    mint = post_bal['mint']
    if mint in WHITELISTED_TOKENS:
        pre_amount = find_pre_balance(mint)
        post_amount = post_bal['uiTokenAmount']['uiAmount']
        if pre_amount != post_amount:
            # Token balance changed = transfer happened
```

### Step 3: Determine Direction
```python
is_incoming = destination == user_address
# OR (for balance change method)
is_incoming = post_amount > pre_amount
```

---

## Common Issues & Solutions

### Issue 1: Token Shows 0 Balance
**Cause**: Only checking `instructions`, missing `innerInstructions`

**Solution**: ✅ Check both places
```python
# Check regular instructions
for instruction in message['instructions']:
    check_for_token()

# Check inner instructions (important!)
for inner in meta['innerInstructions']:
    for instruction in inner['instructions']:
        check_for_token()
```

### Issue 2: Missing Old Transactions
**Cause**: RPC nodes don't keep all historical data

**Solution**: ✅ Fetch maximum signatures (limit: 1000)
```python
{
  "method": "getSignaturesForAddress",
  "params": [address, {"limit": 1000}]  # Max allowed
}
```

### Issue 3: Wrong Token Amounts
**Cause**: Using raw `amount` instead of `uiAmount`

**Solution**: ✅ Use proper decimals
```python
# WRONG
amount = int(info['amount'])  # Raw: 524000000000

# CORRECT
amount = float(info['tokenAmount']['uiAmount'])  # Human: 524000.0
```

---

## Whitelist Token Detection

Our code checks if mint address is whitelisted:

```python
WHITELISTED_SOLANA_TOKENS = {
    'hnstrzjneey2qoyd5d6t48kw2xymyhwvgt61hm5bahj': {
        'symbol': 'HNST',
        'name': 'Honest',
        'decimals': 6
    },
    '2b1kv6dkpanxd5ixfnxcpjxmkwqjjaymczfhsfu24gxo': {
        'symbol': 'PYUSD',
        'name': 'PayPal USD',
        'decimals': 6
    }
}

# Check during parsing
mint = instruction['info']['mint'].lower()
if mint in WHITELISTED_SOLANA_TOKENS:
    token_info = WHITELISTED_SOLANA_TOKENS[mint]
    # This is a whitelisted token transfer!
```

---

## Opening Balance Calculation

For start_date = 2025-04-01, opening_date = 2025-03-31:

```python
# Process all 1000 transactions
for tx in all_transactions:
    tx_date = datetime.fromtimestamp(tx['blockTime'])
    
    # Transactions BEFORE 2025-04-01 contribute to opening balance
    if tx_date <= datetime(2025, 3, 31, 23, 59, 59):
        if token_transfer and token == 'HNST':
            if direction == 'in':
                opening_hnst_balance += amount  # Add incoming
            else:
                opening_hnst_balance -= amount  # Subtract outgoing
        elif sol_transfer:
            if direction == 'in':
                opening_sol_balance += lamports
            else:
                opening_sol_balance -= (lamports + fee)
    
    # Transactions FROM 2025-04-01 to 2025-11-04 are displayed
    elif start_date <= tx_date <= end_date:
        display_transactions.append(tx)
```

Result:
- Opening HNST balance: 524,000 HNST (calculated from all history before April 1)
- Opening SOL balance: Actual amount from all transactions before April 1
- Display: Only transactions from April 1 to November 4
