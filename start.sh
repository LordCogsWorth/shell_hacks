#!/bin/bash

# TravelMaster AI Agent Startup Script

echo "🌍 Starting TravelMaster AI Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "src/travel_agent.py" ]; then
    echo "❌ Please run this script from the shell_hacks directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Create .env file with example values if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cat > .env << EOL
# TravelMaster AI Agent Configuration

# API Keys (replace with your actual keys)
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_secret_here
BOOKING_COM_API_KEY=your_booking_com_api_key_here
GETYOURGUIDE_API_KEY=your_getyourguide_api_key_here
VIATOR_API_KEY=your_viator_api_key_here

# Payment Processing (optional)
STRIPE_PUBLISHABLE_KEY=your_stripe_public_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./travel_master.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Security
SECRET_KEY=your_super_secret_key_here
EOL
    echo "📝 Created .env file with example configuration"
    echo "⚠️  Please update the API keys in .env file for full functionality"
fi

# Start the server
echo "🚀 Starting TravelMaster AI Agent server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "🎤 Voice interaction enabled in the web interface"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd src
python travel_agent.py
