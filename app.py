# =================================================================================
# Main Backend Application: EHR De-Identification Service (Version 1.5 - CORS Enabled)
#
# Author: Joshua (Team Lead)
# Date: October 8, 2025
#
# Description:
# This final, complete version includes all necessary features:
# - Detailed blockchain audit trail with your specific contract details.
# - JWT-based user authentication with role management.
# - CORS support to allow frontend communication.
# =================================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS # Import the CORS library
import spacy
import hashlib
import datetime
import json
from web3 import Web3
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity

# --- 1. Initialization and Configuration ---

# Load spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model... (this may take a minute)")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for your Flask application to allow requests from the frontend
CORS(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "your-super-secret-key-that-you-should-change"
jwt = JWTManager(app)

# --- BLOCKCHAIN CONFIGURATION (WITH YOUR DETAILS) ---
GANACHE_URL = "http://127.0.0.1:7545" 
# YOUR SPECIFIC DEPLOYED CONTRACT ADDRESS
CONTRACT_ADDRESS = "0xd9145CCE52D386f254917e481eB44e9943F39138"
# YOUR SPECIFIC CONTRACT ABI
CONTRACT_ABI = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_action",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_purpose",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_originalHash",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_newHash",
				"type": "string"
			}
		],
		"name": "logEvent",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "recordId",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "action",
				"type": "string"
			}
		],
		"name": "LoggedDetailedEvent",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "recordCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "records",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "action",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "purpose",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "originalDocHash",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "newDocHash",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

# Connect to Ganache and load the contract
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    raise Exception("Error: Could not connect to Ganache.")

audit_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
w3.eth.default_account = w3.eth.accounts[0] # The account that will pay for transactions
print("--- System Ready: Connected to Ganache and Smart Contract Loaded ---")


# --- 2. User Authentication and Core Logic ---

# Simple in-memory user database (replace with a real DB in a production app)
users_db = {
    "dr_strange": {"password": "password123", "role": "medical_professional"},
    "researcher_x": {"password": "password456", "role": "normal_user"}
}

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = users_db.get(username, None)
    if not user or user["password"] != password:
        return jsonify({"msg": "Bad username or password"}), 401
    
    # Convert the dictionary identity into a JSON string
    identity_data = json.dumps({"username": username, "role": user["role"]})
    access_token = create_access_token(identity=identity_data)
    return jsonify(access_token=access_token)

def deidentify_text_with_spacy(text: str) -> str:
    doc = nlp(text)
    new_text = list(text)
    for ent in reversed(doc.ents):
        if ent.label_ in ["PERSON", "DATE", "GPE", "LOC", "ORG"]:
            new_text[ent.start_char:ent.end_char] = f"[{ent.label_}]"
    return "".join(new_text)

def create_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# --- 3. Main API Endpoint ---

@app.route("/deidentify", methods=["POST"])
@jwt_required()
def deidentify_endpoint():
    # Get the identity (a string) and parse it back into a dictionary
    identity_string = get_jwt_identity()
    current_user = json.loads(identity_string)
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON."}), 400
    
    raw_text = request.json.get("text", "")
    purpose = request.json.get("purpose", "General Use")

    clean_text = deidentify_text_with_spacy(raw_text)
    original_hash = create_hash(raw_text)
    deidentified_hash = create_hash(clean_text)

    try:
        tx_hash = audit_contract.functions.logEvent(
            "DE-IDENTIFY",       # The action (WHAT)
            purpose,             # The purpose (WHY)
            original_hash,       # The original fingerprint
            deidentified_hash    # The new fingerprint
        ).transact()
        
        w3.eth.wait_for_transaction_receipt(tx_hash)
        blockchain_status = f"Success! Audit trail logged in transaction: {tx_hash.hex()}"
    except Exception as e:
        blockchain_status = f"Error logging to blockchain: {str(e)}"

    return jsonify({
        "status": "Success",
        "user": current_user,
        "deidentifiedText": clean_text,
        "blockchainAuditStatus": blockchain_status
    })

# --- 4. Running the Application ---

if __name__ == "__main__":
    print("Starting the Advanced De-Identification Service...")
    app.run(debug=True)
