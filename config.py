# app/config.py
import os

class Config:
    """Base configuration. Use environment variables to override."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///education_records.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Read FERNET_KEY from env as string (or None)
    FERNET_KEY = os.environ.get('FERNET_KEY')  # Keep as string; crypto.load_fernet can accept str or bytes

    # Blockchain/Fabric settings
    FABRIC_NETWORK_URL = os.environ.get('FABRIC_NETWORK_URL') or 'http://localhost:7051'
    FABRIC_CA_URL = os.environ.get('FABRIC_CA_URL') or 'http://localhost:7054'
    FABRIC_CHANNEL = os.environ.get('FABRIC_CHANNEL') or 'educationchannel'
    FABRIC_CHAINCODE = os.environ.get('FABRIC_CHAINCODE') or 'education_contract'

    # Institution info
    INSTITUTION_ID = os.environ.get('INSTITUTION_ID') or 'inst123'
    INSTITUTION_NAME = os.environ.get('INSTITUTION_NAME') or 'Cambridge Institute of Technology'

    # Expose helper to get FERNET_KEY as bytes and raise a clear error if missing
    @classmethod
    def get_fernet_key_bytes(cls):
        if not cls.FERNET_KEY:
            raise RuntimeError("FERNET_KEY is not set. Generate one with: from cryptography.fernet import Fernet; Fernet.generate_key() and set FERNET_KEY environment variable.")
        if isinstance(cls.FERNET_KEY, str):
            return cls.FERNET_KEY.encode('utf-8')
        return cls.FERNET_KEY

    @staticmethod
    def init_app(app):
        """Optional app-specific initialization."""
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
