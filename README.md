# Medical Text De-identification & Blockchain Provenance

<p align="center">
  <img src="https://raw.githubusercontent.com/Joshua-Sarkar/Joshua-Sarkar/media/repositories/ehr-deidentification-blockchain/hero.gif" width="100%" alt="Animated medical data privacy project banner" />
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/Joshua-Sarkar/Joshua-Sarkar/media/repositories/ehr-deidentification-blockchain/flow.gif" width="100%" alt="Animated EHR de-identification and blockchain audit workflow" />
</p>

A Flask proof of concept that demonstrates a simple privacy workflow for medical text: detect selected identifying entities, replace them with labels, fingerprint the original and transformed text, and write the hashes and action metadata to a local Ethereum-compatible test chain.

> **Status: academic prototype. Not a clinical or production EHR system.** Do not submit real patient records or protected health information to this demo.

## What it demonstrates

- **Entity-based redaction:** spaCy's `en_core_web_sm` model identifies `PERSON`, `DATE`, `GPE`, `LOC`, and `ORG` entities. The service replaces those spans with labels such as `[PERSON]` and `[DATE]`.
- **Before/after fingerprints:** SHA-256 hashes are calculated for the submitted text and the de-identified output.
- **Blockchain audit event:** the Flask service calls a smart-contract `logEvent` function with the action, purpose, original hash, and transformed hash.
- **JWT-protected processing endpoint:** the browser performs a demo login and sends the token with the de-identification request.
- **Integrity demonstration:** `verify_integrity.py` compares a candidate document's SHA-256 hash with a reference hash.

## How the current code works

1. The browser sends credentials to `POST /login`; the Flask app issues a JWT for the demo user.
2. The browser submits text and a processing purpose to `POST /deidentify` with the bearer token.
3. spaCy detects the supported entity types and replaces them in the text.
4. The backend hashes both versions using SHA-256.
5. Web3.py sends the hashes and audit metadata to the configured contract on Ganache and waits for the transaction receipt.
6. The response displays the transformed text and blockchain transaction status.

## API surface

| Method | Route | Purpose |
|---|---|---|
| POST | `/login` | Demo authentication; returns an access token |
| POST | `/deidentify` | JWT-protected entity replacement and audit logging |

The frontend is a single `index.html` page with login and de-identification views. `test_connection.py` is a separate Ganache connectivity/transaction check.

## Run locally

### Prerequisites

- Python 3.10+ recommended
- Ganache running with an account available
- A deployed contract whose ABI exposes the `logEvent(action, purpose, originalHash, newHash)` function expected by `app.py`

### Install dependencies

The repository's `requirements.txt` is currently empty, so install the imported packages explicitly:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

python -m pip install Flask flask-cors flask-jwt-extended spacy web3
python -m spacy download en_core_web_sm
```

### Configure the local chain

Start Ganache at the endpoint configured in `app.py` (currently `http://127.0.0.1:7545`). Deploy the compatible audit contract and update the contract address/ABI configuration in the backend to match that deployment. The current application expects a local chain and will fail during startup if it cannot connect.

### Start the backend

```bash
python app.py
```

Open `index.html` in a browser. The page currently calls `http://127.0.0.1:5000`; change that base URL if the backend runs elsewhere.

## Repository map

| File | Responsibility |
|---|---|
| `app.py` | Flask app, spaCy redaction, JWT login, hashing, Web3 contract call |
| `index.html` | Login and text de-identification interface |
| `test_connection.py` | Ganache connection and sample transaction check |
| `verify_integrity.py` | SHA-256 integrity comparison demonstration |
| `requirements.txt` | Currently empty; dependencies are listed above |

## Important limitations and next steps

- The entity recognizer is not a guarantee of complete de-identification. Names, dates, IDs, and contextual identifiers can be missed or misclassified.
- The current demo user store is in memory and contains sample credentials. Replace it with a proper identity store, password hashing, role management, and rate limiting before any wider use.
- JWT signing configuration, blockchain endpoint, contract address, and contract ABI should come from environment/configuration, not source literals.
- A blockchain hash proves that a specific byte sequence matches a recorded fingerprint; it does not prove that the source text was clinically correct, lawfully collected, or fully anonymised.
- The repository currently has no contract source or deployment script. Supply and audit those separately before relying on the chain integration.
- Add automated tests for entity offsets, Unicode, repeated entities, empty input, malformed requests, and chain failures.

## Safety note

This project is for learning and demonstration. It has not been validated for healthcare compliance, clinical workflows, or production patient-data processing.

---

<p align="center"><sub>Privacy is a pipeline, not a single redaction function.</sub></p>
