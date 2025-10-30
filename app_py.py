from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
from datetime import datetime

from crypto import CryptoManager, compute_sha256
from blockchain_adapter import BlockchainAdapter
from models import init_db, get_session, Student, Record, Transaction, VerifierRequest
from config import config
from merkle import MerkleTree

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])
CORS(app)

# Initialize database
init_db(app.config['SQLALCHEMY_DATABASE_URI'])

# Initialize crypto manager
fernet_key = os.environ.get('FERNET_KEY') or app.config.get('FERNET_KEY')
if not fernet_key:
    raise RuntimeError("FERNET_KEY is not set. Generate one using Fernet.generate_key() and export it.")
crypto_manager = CryptoManager(fernet_key)

# Initialize blockchain adapter
blockchain = BlockchainAdapter(
    network_url=app.config['FABRIC_NETWORK_URL'],
    channel=app.config['FABRIC_CHANNEL'],
    chaincode=app.config['FABRIC_CHAINCODE'],
    issuer_id=app.config['INSTITUTION_ID']
)

# ------------------------------
# ROUTES
# ------------------------------

@app.route('/')
def index():
    """Home page"""
    return jsonify({
        'message': 'Blockchain-Based Education Data Management System',
        'status': 'running',
        'institution': app.config['INSTITUTION_NAME']
    })

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student record"""
    try:
        data = request.json

        if not data.get('student_id') or not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Missing required fields'}), 400

        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])

        existing = session.query(Student).filter_by(student_id=data['student_id']).first()
        if existing:
            session.close()
            return jsonify({'error': 'Student already exists'}), 409

        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data['email'],
            public_metadata=data.get('public_metadata', {})
        )

        session.add(student)
        session.commit()
        result = student.to_dict()
        session.close()

        return jsonify({'status': 'created', 'student': result}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get student details"""
    try:
        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        student = session.query(Student).filter_by(student_id=student_id).first()

        if not student:
            session.close()
            return jsonify({'error': 'Student not found'}), 404

        result = student.to_dict()
        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/issue', methods=['POST'])
def issue_record():
    """Issue a new academic record"""
    try:
        data = request.json

        if not data.get('student_id') or not data.get('payload'):
            return jsonify({'error': 'Missing required fields'}), 400

        student_id = data['student_id']
        payload = data['payload']

        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        student = session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            session.close()
            return jsonify({'error': 'Student not found'}), 404

        ciphertext, payload_hash = crypto_manager.encrypt(payload)
        record_id = f"rec_{uuid.uuid4().hex[:16]}"

        record = Record(
            record_id=record_id,
            student_id=student_id,
            encrypted_payload=ciphertext,
            payload_hash=payload_hash
        )

        session.add(record)
        session.commit()

        try:
            tx_id = blockchain.submit_issue_transaction(
                record_id=record_id,
                anchor_hash=payload_hash,
                issuer=app.config['INSTITUTION_ID']
            )

            record.tx_id = tx_id
            session.commit()

            transaction = Transaction(
                tx_id=tx_id,
                operation='ISSUE',
                issuer_id=app.config['INSTITUTION_ID'],
                merkle_root=payload_hash
            )
            session.add(transaction)
            session.commit()

        except Exception as bc_error:
            session.rollback()
            session.close()
            return jsonify({'error': f'Blockchain error: {str(bc_error)}'}), 500

        result = record.to_dict()
        session.close()

        return jsonify({
            'status': 'issued',
            'record_id': record_id,
            'tx_id': tx_id,
            'payload_hash': payload_hash
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>', methods=['GET'])
def get_record(record_id):
    """Get record details (encrypted)"""
    try:
        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        record = session.query(Record).filter_by(record_id=record_id).first()

        if not record:
            session.close()
            return jsonify({'error': 'Record not found'}), 404

        result = record.to_dict()
        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/decrypt', methods=['GET'])
def decrypt_record(record_id):
    """Decrypt and return record payload (authorized access only)"""
    try:
        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        record = session.query(Record).filter_by(record_id=record_id).first()

        if not record:
            session.close()
            return jsonify({'error': 'Record not found'}), 404

        plaintext = crypto_manager.decrypt(record.encrypted_payload)
        result = {
            'record_id': record.record_id,
            'student_id': record.student_id,
            'payload': plaintext,
            'payload_hash': record.payload_hash,
            'tx_id': record.tx_id,
            'timestamp': record.timestamp.isoformat() if record.timestamp else None
        }

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/verify/<record_id>', methods=['GET'])
def verify_record(record_id):
    """Verify a record's integrity"""
    try:
        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        record = session.query(Record).filter_by(record_id=record_id).first()

        if not record:
            session.close()
            return jsonify({'error': 'Record not found'}), 404

        plaintext = crypto_manager.decrypt(record.encrypted_payload)
        recomputed_hash = compute_sha256(plaintext)

        onchain_data = blockchain.query_anchor(record_id)
        verified = (recomputed_hash == record.payload_hash)

        request_id = f"req_{uuid.uuid4().hex[:16]}"
        ver_request = VerifierRequest(
            request_id=request_id,
            requester_id='system',
            record_id=record_id,
            supplied_proof=recomputed_hash,
            status='VALID' if verified else 'INVALID'
        )
        session.add(ver_request)
        session.commit()

        result = {
            'verified': verified,
            'record_id': record_id,
            'payload_hash': record.payload_hash,
            'recomputed_hash': recomputed_hash,
            'onchain_anchor': onchain_data,
            'tx_id': record.tx_id
        }

        session.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch-issue', methods=['POST'])
def batch_issue():
    """Issue multiple records in a batch using Merkle tree"""
    try:
        data = request.json
        records_data = data.get('records', [])

        if not records_data:
            return jsonify({'error': 'No records provided'}), 400

        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        merkle_tree = MerkleTree()
        issued_records = []

        for rec_data in records_data:
            student_id = rec_data.get('student_id')
            payload = rec_data.get('payload')

            if not student_id or not payload:
                continue

            ciphertext, payload_hash = crypto_manager.encrypt(payload)
            record_id = f"rec_{uuid.uuid4().hex[:16]}"

            merkle_tree.add_leaf(payload_hash)

            record = Record(
                record_id=record_id,
                student_id=student_id,
                encrypted_payload=ciphertext,
                payload_hash=payload_hash
            )

            session.add(record)
            issued_records.append(record)

        merkle_root_hash = merkle_tree.compute_root()
        tx_id = blockchain.submit_issue_transaction(
            record_id='batch_' + uuid.uuid4().hex[:16],
            anchor_hash=merkle_root_hash,
            issuer=app.config['INSTITUTION_ID']
        )

        for record in issued_records:
            record.tx_id = tx_id

        transaction = Transaction(
            tx_id=tx_id,
            operation='BATCH_ISSUE',
            issuer_id=app.config['INSTITUTION_ID'],
            merkle_root=merkle_root_hash
        )
        session.add(transaction)
        session.commit()

        result = {
            'status': 'batch_issued',
            'count': len(issued_records),
            'merkle_root': merkle_root_hash,
            'tx_id': tx_id,
            'records': [r.to_dict() for r in issued_records]
        }

        session.close()
        return jsonify(result), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions"""
    try:
        session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        transactions = session.query(Transaction).order_by(Transaction.timestamp.desc()).all()

        result = [t.to_dict() for t in transactions]
        session.close()

        return jsonify({'transactions': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'blockchain_connected': not blockchain.mock_mode
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Run the application
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
