# blockchain_adapter.py
"""
Mock Blockchain Adapter for the EduChain System.
Simulates interaction with a blockchain network (e.g., Hyperledger Fabric).
"""

from datetime import datetime
import random
import hashlib

class BlockchainAdapter:
    def __init__(self, network_url, channel, chaincode, issuer_id, mock_mode=True):
        """
        Initialize blockchain adapter.
        In mock_mode, no actual blockchain network is used.
        """
        self.network_url = network_url
        self.channel = channel
        self.chaincode = chaincode
        self.issuer_id = issuer_id
        self.mock_mode = True  # Always true for demo
        print("[BlockchainAdapter] Initialized (mock_mode=True)")

    # --------------------------
    # FIX: Add this method ↓↓↓
    # --------------------------
    def submit_issue_transaction(self, record_id, anchor_hash, issuer):
        """
        Simulate submitting an issue transaction to blockchain.
        Returns a mock transaction ID.
        """
        print(f"[BlockchainAdapter] submit_issue_transaction called for {record_id}")
        tx_id = f"tx_{int(datetime.now().timestamp())}_{random.randint(100,999)}"
        print(f"[BlockchainAdapter] Simulated blockchain tx_id: {tx_id}")
        return tx_id

    # Optional: For batch issuing (used in batch_issue route)
    def submit_batch_transaction(self, records, merkle_root, issuer):
        tx_id = f"tx_batch_{int(datetime.now().timestamp())}_{random.randint(100,999)}"
        print(f"[BlockchainAdapter] Simulated batch tx_id: {tx_id}")
        return tx_id

    def query_anchor(self, record_id):
        """
        Mock querying anchor hash from blockchain.
        Returns a pseudo hash value.
        """
        mock_hash = hashlib.sha256(record_id.encode()).hexdigest()
        print(f"[BlockchainAdapter] query_anchor({record_id}) -> {mock_hash}")
        return {
            "record_id": record_id,
            "anchor_hash": mock_hash,
            "block_number": random.randint(1000, 9999),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_transaction_history(self):
        """
        Mock blockchain transaction history.
        """
        history = [
            {
                "tx_id": f"tx_{i}",
                "issuer": self.issuer_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "confirmed"
            }
            for i in range(3)
        ]
        print("[BlockchainAdapter] Returning mock transaction history")
        return history
