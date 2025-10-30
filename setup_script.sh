#!/bin/bash

echo "=========================================="
echo "Blockchain Education System Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✓ Virtual environment created"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Generate Fernet key
echo "Generating encryption key..."
python3 << EOF
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(f"\nYour Fernet Key: {key.decode()}")
print("\nAdd this to your .env file as:")
print(f"FERNET_KEY={key.decode()}")
EOF

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOL'
SECRET_KEY=dev-secret-key-change-in-production
FERNET_KEY=your-generated-key-here
DEBUG=True
DATABASE_URL=sqlite:///education_records.db
INSTITUTION_ID=inst123
INSTITUTION_NAME=Cambridge Institute of Technology
FABRIC_NETWORK_URL=http://localhost:7051
FABRIC_CA_URL=http://localhost:7054
FABRIC_CHANNEL=educationchannel
FABRIC_CHAINCODE=education_contract
EOL
    echo "✓ .env file created (please update with your Fernet key)"
fi

# Initialize database
echo "Initializing database..."
cd app
python3 << EOF
from models import init_db
init_db()
print("✓ Database initialized")
EOF
cd ..

# Create necessary directories
mkdir -p data
mkdir -p logs
mkdir -p tests

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update the .env file with your generated Fernet key"
echo "2. Run the application:"
echo "   python app/app.py"
echo ""
echo "3. Access the API at http://localhost:5000"
echo ""
echo "For development with mock blockchain:"
echo "   The system will run in mock mode by default"
echo ""
echo "For production with Hyperledger Fabric:"
echo "   1. Set up Fabric network using docker-compose.yml"
echo "   2. Deploy chaincode from chaincode/education_contract.go"
echo "   3. Set mock_mode = False in blockchain_adapter.py"
echo ""
echo "=========================================="