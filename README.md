# TravelMaster AI Agent 🌍✈️

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen.svg)

<!-- markdownlint-disable no-inline-html -->

<div align="center">
   <h1>🚀 TravelMaster AI Agent</h1>
   <h3>
      AI-powered travel planning agent that books flights, hotels, and activities while staying within your budget.
      Features voice interaction and complete itinerary generation using the Agent2Agent (A2A) protocol.
   </h3>
</div>

<!-- markdownlint-enable no-inline-html -->

---

## ✨ Features

### 🧠 AI-Powered Travel Planning
- **Smart Itinerary Generation:** Creates complete vacation plans optimized for your budget and preferences
- **Voice Interaction:** Speak your travel desires using natural language processing
- **Budget Optimization:** Automatically allocates budget across flights, hotels, and activities
- **Preference Learning:** Understands luxury, budget, adventure, cultural, and relaxation preferences

### 🌐 Global Booking Integration
- **Flight Booking:** Integration with Amadeus, Skyscanner APIs for worldwide flights
- **Hotel Reservations:** Booking.com and Hotels.com integration for accommodation
- **Activity Planning:** GetYourGuide and Viator APIs for tours and experiences
- **Real-time Pricing:** Live pricing and availability from multiple providers

### 🎤 Voice-Enabled Interface
- **Speech-to-Text:** Tell the AI about your dream trip using your voice
- **Natural Language Processing:** Understands complex travel requests
- **Smart Parsing:** Extracts destinations, dates, budgets, and preferences from speech

### 💻 Modern Web Interface
- **Responsive Design:** Beautiful UI that works on desktop and mobile
- **Real-time Updates:** Live itinerary generation with progress indicators
- **Interactive Planning:** Drag-and-drop schedule customization
- **Shareable Itineraries:** Export and share your travel plans

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Modern web browser (Chrome, Firefox, Safari)
- Internet connection for API integrations

### ⚡ One-Command Setup

```bash
# Clone and start the TravelMaster AI Agent
git clone https://github.com/LordCogsWorth/shell_hacks.git
cd shell_hacks
./start.sh
```

The startup script will:
1. Create a Python virtual environment
2. Install all dependencies
3. Generate configuration files
4. Start the AI agent server

### 🌐 Access the Application

- **Web Interface:** http://localhost:8000
- **Voice Interaction:** Click the microphone button and speak your travel plans
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

## 💬 Voice Commands

Try saying things like:
- *"I want to go to Paris with a budget of 3000 dollars for a luxury trip"*
- *"Plan an adventure vacation to Tokyo for 2 people in December"*
- *"Find me a budget-friendly cultural trip to Rome next month"*

## 🔧 Configuration

### API Keys Setup

Update the `.env` file with your API keys for full functionality:

```bash
# Flight booking APIs
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret

# Hotel booking APIs
BOOKING_COM_API_KEY=your_booking_key

# Activity booking APIs
GETYOURGUIDE_API_KEY=your_getyourguide_key
VIATOR_API_KEY=your_viator_key

# Payment processing (optional)
STRIPE_PUBLISHABLE_KEY=your_stripe_key
```

### Development Mode

```bash
# Manual setup for development
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the agent
cd src
python travel_agent.py
```

## 🎯 Usage Examples

### 1. Web Interface Planning

1. Open http://localhost:8000
2. Fill in travel details or use voice input
3. Click "Plan My Dream Trip"
4. Review your AI-generated itinerary
5. Export or modify as needed

### 2. Voice Planning

1. Click the microphone button 🎤
2. Speak naturally: *"I want a 5-day cultural trip to Barcelona for under 2500 dollars"*
3. The AI will parse your speech and fill the form
4. Review and submit for planning

### 3. API Integration

```python
import httpx
import asyncio

async def plan_trip():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/plan-trip",
            json={
                "destination": "Paris, France",
                "departure_location": "New York, NY",
                "start_date": "2024-06-15",
                "end_date": "2024-06-22",
                "budget": 3500,
                "travelers": 2,
                "preferences": ["cultural", "luxury"]
            }
        )
        return response.json()

# Run the planning
itinerary = asyncio.run(plan_trip())
print(f"Total cost: ${itinerary['total_cost']}")
```

---

## 🤝 Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get involved.

---

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for more details.
# Test push
