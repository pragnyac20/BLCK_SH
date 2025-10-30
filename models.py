from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Student(Base):
    """Student entity model"""
    __tablename__ = 'students'
    
    student_id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    public_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    records = relationship("Record", back_populates="student")
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'public_metadata': self.public_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Record(Base):
    """Academic record entity model"""
    __tablename__ = 'records'
    
    record_id = Column(String(100), primary_key=True)
    student_id = Column(String(50), ForeignKey('students.student_id'), nullable=False)
    encrypted_payload = Column(LargeBinary, nullable=False)
    payload_hash = Column(String(64), nullable=False)
    version = Column(Integer, default=1)
    tx_id = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    student = relationship("Student", back_populates="records")
    
    def to_dict(self):
        return {
            'record_id': self.record_id,
            'student_id': self.student_id,
            'payload_hash': self.payload_hash,
            'version': self.version,
            'tx_id': self.tx_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Transaction(Base):
    """Blockchain transaction log"""
    __tablename__ = 'transactions'
    
    tx_id = Column(String(200), primary_key=True)
    operation = Column(String(50), nullable=False)
    issuer_id = Column(String(100), nullable=False)
    merkle_root = Column(String(64))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'tx_id': self.tx_id,
            'operation': self.operation,
            'issuer_id': self.issuer_id,
            'merkle_root': self.merkle_root,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class VerifierRequest(Base):
    """Verification request log"""
    __tablename__ = 'verifier_requests'
    
    request_id = Column(String(100), primary_key=True)
    requester_id = Column(String(100), nullable=False)
    record_id = Column(String(100), ForeignKey('records.record_id'), nullable=False)
    supplied_proof = Column(String(64))
    status = Column(String(20))  # VALID, INVALID, PENDING
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'requester_id': self.requester_id,
            'record_id': self.record_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

# Database initialization
def init_db(db_uri='sqlite:///education_records.db'):
    """Initialize the database"""
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

# Create a session factory
def get_session(db_uri='sqlite:///education_records.db'):
    """Get a database session"""
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    return Session()