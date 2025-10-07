from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# 1. Check the connection
print(f"Is connected to Ganache? {w3.is_connected()}")

# 2. Check the accounts
accounts = w3.eth.accounts
if not accounts:
    print("Error: No accounts found. Is Ganache running?")
else:
    print(f"Found {len(accounts)} accounts.")
    
    # 3. Try to send a simple transaction
    try:
        print("Sending a test transaction from Account 0 to Account 1...")
        tx_hash = w3.eth.send_transaction({
            'from': accounts[0],
            'to': accounts[1],
            'value': w3.to_wei(1, 'gwei') # Send a tiny amount
        })
        
        # Wait for it to be mined
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"SUCCESS! Test transaction was successful. Hash: {tx_hash.hex()}")
        print("Check the 'Transactions' tab in Ganache now.")

    except Exception as e:
        print(f"Transaction FAILED: {e}")
