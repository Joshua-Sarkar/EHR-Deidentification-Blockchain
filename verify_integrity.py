# ==============================================================================
# Data Integrity Verification Tool (Version 1.0)
#
# Author: Joshua (Team Lead)
# Date: October 8, 2025
#
# Description:
# This script simulates an audit by comparing the hash of a current data
# record against the immutable hash stored on the blockchain. It serves to
# practically demonstrate how blockchain prevents undetected data tampering.
# ==============================================================================

import hashlib

def create_hash(text: str) -> str:
    """Calculates the SHA-256 hash of a given text."""
    return hashlib.sha256(text.encode()).hexdigest()

def verify_data_integrity(true_hash_from_blockchain: str, data_to_check: str):
    """
    Compares the hash of the data-to-check against the true hash from the blockchain.
    """
    print(f"--- Verifying Data Integrity ---")
    print(f"True Hash (from Blockchain): {true_hash_from_blockchain}")
    
    # Calculate the hash of the data we are currently checking
    current_hash = create_hash(data_to_check)
    print(f"Current Data's Hash:         {current_hash}")
    
    # Compare the two hashes
    if true_hash_from_blockchain == current_hash:
        print("\n[SUCCESS] Verification Passed: The data has NOT been tampered with.")
    else:
        print("\n[ALERT] TAMPERING DETECTED: The data does not match the blockchain record!")

# --- Main Demonstration Block ---

if __name__ == "__main__":
    
    # --- SCENARIO SETUP ---
    
    # Paste the TRUE hash you copied from your app's output here
    TRUE_ORIGINAL_HASH = " 3a166cec9d810088c8161945d083ec8fc6baa6a3acbd5b70a2f03d290650e962"

    # This represents the current state of the document in our database
    unaltered_document = "Patient John Smith was admitted on October 8, 2025."
    
    # This represents the document AFTER a hacker has changed it
    tampered_document = "Patient Jane Doe was admitted on October 8, 2025."

    # --- DEMONSTRATION ---
    
    # 1. First, let's audit the unaltered document. It should pass.
    print("="*40)
    print("AUDITING THE UNALTERED DOCUMENT...")
    print("="*40)
    verify_data_integrity(TRUE_ORIGINAL_HASH, unaltered_document)
    
    print("\n" + "#"*40 + "\n")

    # 2. Now, let's audit the tampered document. It should fail.
    print("="*40)
    print("AUDITING THE TAMPERED DOCUMENT...")
    print("="*40)
    verify_data_integrity(TRUE_ORIGINAL_HASH, tampered_document)

