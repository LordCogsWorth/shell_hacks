"""
Simplified Real API Flight Agent - Returns actual flight data from Amadeus API
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, date
from decimal import Decimal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our real API manager
REAL_API_AVAILABLE = False
travel_apis = None
FlightSearchParams = None
TravelAPIManager = None

try:
    from travel_apis import TravelAPIManager, FlightSearchParams
    REAL_API_AVAILABLE = True
    print("✅ Real API imports successful")
except ImportError as e:
    print(f"⚠️ Could not import TravelAPIManager: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Real API Flight Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API manager
if REAL_API_AVAILABLE and TravelAPIManager:
    travel_apis = TravelAPIManager()
    print("✅ Real API Flight Agent - Connected to Amadeus")
else:
    travel_apis = None
    print("❌ No real APIs available - using enhanced mock data")

@app.post("/api/search-flights")
async def search_flights(request_data: Dict[str, Any]):
    """Search for flights using REAL APIs"""
    
    departure = request_data.get('departure_location', 'New York, NY')
    destination = request_data.get('destination', 'Paris, France')
    start_date = request_data.get('start_date', '2025-11-15')
    travelers = request_data.get('travelers', 2)
    budget = request_data.get('budget', 1200)
    
    logger.info(f"🔍 REAL API Flight Search: {departure} → {destination} on {start_date}")
    
    try:
        if travel_apis and REAL_API_AVAILABLE and FlightSearchParams:
            # Use REAL Amadeus API
            search_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            flight_budget = float(budget) * 0.4 / travelers if budget else 600.0
            
            params = FlightSearchParams(
                origin=departure,
                destination=destination,
                departure_date=search_date,
                passengers=travelers,
                max_price=Decimal(str(flight_budget))
            )
            
            real_flights = await travel_apis.flight_api.search_flights(params)
            
            # Convert to standard format with negotiation capabilities
            flights_with_negotiation = []
            for flight in real_flights:
                flight_dict = {
                    "flight_id": f"REAL_{flight.get('id', datetime.now().timestamp())}",
                    "airline": flight.get('airline', 'Unknown Airline'),
                    "departure_airport": flight.get('departure_airport', departure),
                    "arrival_airport": flight.get('arrival_airport', destination),
                    "departure_time": flight.get('departure_time', f"{start_date}T08:00:00"),
                    "arrival_time": flight.get('arrival_time', f"{start_date}T12:00:00"),
                    "price": float(flight.get('price', 450)),
                    "booking_class": flight.get('booking_class', 'Economy'),
                    "available_seats": flight.get('available_seats', 10),
                    "agent_id": "real-api-flight-agent",
                    "negotiable": True,
                    "min_price": float(flight.get('price', 450)) * 0.9,
                    "negotiation_expires": f"{start_date}T20:00:00",
                    "real_api_data": True
                }
                flights_with_negotiation.append(flight_dict)
            
            logger.info(f"✅ Found {len(flights_with_negotiation)} REAL flights from Amadeus API")
            
            return {
                "success": True,
                "agent_id": "real-api-flight-agent",
                "flights": flights_with_negotiation,
                "total_found": len(flights_with_negotiation),
                "negotiation_available": True,
                "api_source": "Amadeus Real API"
            }
        
        else:
            # Enhanced mock data with real airline names
            logger.info("🔄 Using enhanced mock data with real airline names")
            
            mock_flights = [
                {
                    "flight_id": f"AA_{datetime.now().timestamp()}",
                    "airline": "American Airlines",
                    "departure_airport": departure,
                    "arrival_airport": destination,
                    "departure_time": f"{start_date}T06:00:00",
                    "arrival_time": f"{start_date}T19:30:00",
                    "price": 485.0,
                    "booking_class": "Economy",
                    "available_seats": 23,
                    "agent_id": "real-api-flight-agent",
                    "negotiable": True,
                    "min_price": 436.5,
                    "negotiation_expires": f"{start_date}T20:00:00",
                    "real_api_data": False
                },
                {
                    "flight_id": f"DL_{datetime.now().timestamp()}",
                    "airline": "Delta Air Lines",
                    "departure_airport": departure,
                    "arrival_airport": destination,
                    "departure_time": f"{start_date}T09:15:00",
                    "arrival_time": f"{start_date}T22:45:00",
                    "price": 425.0,
                    "booking_class": "Economy",
                    "available_seats": 15,
                    "agent_id": "real-api-flight-agent",
                    "negotiable": True,
                    "min_price": 382.5,
                    "negotiation_expires": f"{start_date}T20:00:00",
                    "real_api_data": False
                },
                {
                    "flight_id": f"AF_{datetime.now().timestamp()}",
                    "airline": "Air France",
                    "departure_airport": departure,
                    "arrival_airport": destination,
                    "departure_time": f"{start_date}T14:30:00",
                    "arrival_time": f"{start_date}T03:15+1",
                    "price": 395.0,
                    "booking_class": "Economy",
                    "available_seats": 8,
                    "agent_id": "real-api-flight-agent",
                    "negotiable": True,
                    "min_price": 355.5,
                    "negotiation_expires": f"{start_date}T20:00:00",
                    "real_api_data": False
                }
            ]
            
            return {
                "success": True,
                "agent_id": "real-api-flight-agent", 
                "flights": mock_flights,
                "total_found": len(mock_flights),
                "negotiation_available": True,
                "api_source": "Enhanced Mock Data"
            }
            
    except Exception as e:
        logger.error(f"❌ Flight search failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent_id": "real-api-flight-agent",
            "flights": [],
            "total_found": 0
        }

@app.get("/.well-known/agent")
async def agent_info():
    """A2A agent discovery endpoint"""
    return {
        "agent_id": "real-api-flight-agent",
        "name": "Real API Flight Agent",
        "version": "1.0.0",
        "capabilities": ["flight_search", "real_api_integration"],
        "endpoints": {
            "search_flights": "/api/search-flights"
        },
        "description": "Flight search agent using real Amadeus API integration"
    }

if __name__ == "__main__":
    print("🛩️ Starting Real API Flight Agent...")
    print("✈️ Amadeus API Integration Enabled" if REAL_API_AVAILABLE else "⚠️ Using Enhanced Mock Data")
    print("📍 Available at: http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
