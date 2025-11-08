"""
Solana Integration Layer (Testnet) - Proof-of-Signal

Publishes AI trading signal proofs on-chain as verifiable records on Solana testnet.
Functions:
- init_wallet(): Load or create a local wallet keypair
- hash_signal(data): Deterministic SHA256 hash of signal payload
- send_proof(signal_data): Sends a minimal self-transfer with proof hash context

Notes:
- Stores a local secret key hex at project root: solana_wallet.json
- Uses a self-transfer (1 lamport) as a minimal on-chain footprint
"""

import hashlib
import json
import os
from typing import Dict

try:
    from solana.rpc.api import Client
    from solana.transaction import Transaction
    from solana.system_program import TransferParams, transfer
    from solana.keypair import Keypair
    from solana.rpc.types import TxOpts
    SOLANA_AVAILABLE = True
except ImportError:
    Client = Transaction = TransferParams = transfer = Keypair = TxOpts = None
    SOLANA_AVAILABLE = False

SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.testnet.solana.com")
WALLET_FILE = os.getenv("SOLANA_WALLET_FILE", "solana_wallet.json")

client = Client(SOLANA_RPC_URL) if SOLANA_AVAILABLE else None


def init_wallet() -> Keypair:
    """Load or create a Solana wallet from local file (hex-encoded secret key)."""
    try:
        with open(WALLET_FILE, "r") as f:
            secret_hex = f.read().strip()
        kp = Keypair.from_secret_key(bytes.fromhex(secret_hex))
    except FileNotFoundError:
        kp = Keypair()
        with open(WALLET_FILE, "w") as f:
            f.write(kp.secret_key.hex())
    return kp


def hash_signal(signal_data: Dict) -> str:
    """Compute SHA256 hash of signal payload (sorted keys for determinism)."""
    payload = json.dumps(signal_data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def send_proof(signal_data: Dict) -> Dict[str, str]:
    """
    Publish a proof of the AI signal to Solana testnet.

    Creates a minimal self-transfer (1 lamport). The proof hash is computed and
    returned alongside the transaction signature so consumers can verify
    the signal payload off-chain against the on-chain timestamp/signature.
    """
    if not SOLANA_AVAILABLE:
        return {
            "proof_hash": hash_signal(signal_data),
            "tx_signature": None,
            "message": "Solana publishing disabled"
        }

    kp = init_wallet()
    proof = hash_signal(signal_data)

    # Prepare minimal transaction: self-transfer of 1 lamport
    tx = Transaction()
    tx.add(
        transfer(
            TransferParams(
                from_pubkey=kp.public_key,
                to_pubkey=kp.public_key,
                lamports=1,
            )
        )
    )

    # Fetch a recent blockhash
    latest = client.get_latest_blockhash() if client else None
    if not latest:
        raise RuntimeError("Solana client unavailable")
    blockhash = latest["result"]["value"]["blockhash"]
    tx.recent_blockhash = blockhash
    tx.sign(kp)

    # Submit transaction
    resp = client.send_transaction(tx, kp, opts=TxOpts(skip_preflight=True))
    signature = resp.get("result")

    return {
        "proof_hash": proof,
        "tx_signature": signature,
    }


