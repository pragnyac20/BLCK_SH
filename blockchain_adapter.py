"""
blockchain_adapter_py.py
-------------------------------------
This module abstracts blockchain (Hyperledger Fabric) interactions.

If MOCK_BLOCKCHAIN is set (default True), it will simulate blockchain
transactions locally without needing a Fabric network.
"""

import os
import json
import requests
import uuid
from datetime import datetime


class BlockchainAdapter:
    """
    A helper class that abstracts interaction with a Fabric blockchain network.
    It supports both real mode (using REST API calls) and mock mode for testing.
    """

    def __init__(self, network_url, channel, chaincode, issuer_id, mock_mode=None):
        self.network_url = network_url
        self.channel = channel
        self.chaincode = chaincode
        self.issuer_id = issuer_id

        # Allow environment override
        env_val = os.environ.get("MOCK_BLOCKCHAIN")
        if mock_mode is not None:
            self.mock_mode = mock_mode
        elif env_val is not None:
            self.mock_mode = env_val.lower() not in ("0", "false", "no")
        else:
            # Default to True for local testing
            self.mock_mode = True

        print(f"[BlockchainAdapter] Initialized (mock_mode={self.mock_mode})")

    # -------------------------------------------------------------------------
    # Utility Functions
    # -------------------------------------------------------------------------
    def _mock_transaction(self, function_name, payload):
        """
        Simulates a blockchain transaction and returns a mock response.
        """
        tx_id = f"tx_{uuid.uuid4().hex[:10]}"
        response = {
            "transaction_id": tx_id,
            "function": function_name,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "issuer_id": self.issuer_id,
            "status": "SUCCESS",
        }
        print(f"[BlockchainAdapter] Mock transaction executed: {tx_id}")
        return response

    def _post_request(self, endpoint, data):
        """
        Internal helper to send POST requests to the blockchain network.
        """
        try:
            url = f"{self.network_url}/{endpoint}"
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[BlockchainAdapter] ERROR during POST {endpoint}: {e}")
            return {"status": "ERROR", "message": str(e)}

    # -------------------------------------------------------------------------
    # Blockchain Functions
    # -------------------------------------------------------------------------
    def invoke_chaincode(self, function_name, args):
        """
        Invokes a transaction on the blockchain.

        :param function_name: Name of the chaincode function to call
        :param args: Dictionary containing arguments for the function
        :return: Response from the blockchain or mock data
        """
        if self.mock_mode:
            return self._mock_transaction(function_name, args)

        # Example for Fabric REST API call
        payload = {
            "channel": self.channel,
            "chaincode": self.chaincode,
            "function": function_name,
            "args": json.dumps(args),
        }
        print(f"[BlockchainAdapter] Invoking chaincode '{function_name}' (real mode)...")
        return self._post_request("invoke", payload)

    def query_chaincode(self, function_name, args):
        """
        Queries data from the blockchain.

        :param function_name: Name of the chaincode function
        :param args: Dictionary of arguments for the query
        :return: Response data or mock result
        """
        if self.mock_mode:
            mock_data = {
                "query_result": {
                    "record_id": args.get("record_id"),
                    "status": "VERIFIED",
                    "issuer_id": self.issuer_id,
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            print(f"[BlockchainAdapter] Mock query executed: {mock_data}")
            return mock_data

        payload = {
            "channel": self.channel,
            "chaincode": self.chaincode,
            "function": function_name,
            "args": json.dumps(args),
        }
        print(f"[BlockchainAdapter] Querying chaincode '{function_name}' (real mode)...")
        return self._post_request("query", payload)

    # -------------------------------------------------------------------------
    # High-level Use-case Wrappers
    # -------------------------------------------------------------------------
    def issue_certificate(self, record_id, student_name, course_name, grade):
        """
        Issues a digital certificate record to the blockchain.
        """
        payload = {
            "record_id": record_id,
            "student_name": student_name,
            "course_name": course_name,
            "grade": grade,
            "issuer_id": self.issuer_id,
            "issued_at": datetime.utcnow().isoformat() + "Z",
        }
        print(f"[BlockchainAdapter] Issuing certificate for record: {record_id}")
        return self.invoke_chaincode("issueCertificate", payload)

    def verify_record(self, record_id):
        """
        Verifies whether a record exists and is valid on the blockchain.
        """
        print(f"[BlockchainAdapter] Verifying record: {record_id}")
        return self.query_chaincode("verifyRecord", {"record_id": record_id})

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------
    def check_connection(self):
        """
        Checks if the blockchain network (or mock) is reachable.
        """
        if self.mock_mode:
            return {"status": "MOCK_MODE_ACTIVE", "connected": True}

        try:
            url = f"{self.network_url}/health"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return {"status": "CONNECTED", "response": response.json()}
        except requests.RequestException as e:
            print(f"[BlockchainAdapter] Health check failed: {e}")
            return {"status": "DISCONNECTED", "error": str(e)}
