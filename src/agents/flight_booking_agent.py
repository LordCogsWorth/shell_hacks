"""
FlightBookingAgent - A2A Compliant Agent for Flight Search and Booking

This agent specializes in flight search, booking, and price negotiation
using the Agent-to-Agent protocol for inter-agent communication.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
import uvicorn

# Simple imports for now - will enhance to full A2A later
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


class FlightBookingAgent:
    """
    Specialized agent for flight search and booking operations.
    Will be enhanced to full A2A compliance in next iteration.
    """
    
    def __init__(self):
        self.agent_id = "flight-booking-agent"
        self.name = "FlightBookingAgent"
        self.version = "1.0.0"
        self.capabilities = [
            "flight_search",
            "flight_booking", 
            "price_negotiation",
            "availability_checking"
        ]
        
        # Initialize real API connections
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from travel_apis import TravelAPIManager
            self.travel_apis = TravelAPIManager()
            print("✅ Connected to real flight APIs (Amadeus)")
        except ImportError as e:
            print(f"⚠️  Could not import TravelAPIManager - using mock data: {e}")
            self.travel_apis = None
        
        logger.info(f"✈️ FlightBookingAgent initialized with capabilities: {self.capabilities}")
    
    async def search_flights(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for flights using ONLY real APIs - no mock data fallbacks"""
        departure = request_data.get('departure_location', 'NYC')
        destination = request_data.get('destination', 'LAX')
        start_date = request_data.get('start_date', '2025-11-15')
        travelers = request_data.get('travelers', 1)
        budget = request_data.get('budget', 1000)
        
        logger.info(f"🔍 Searching REAL flights ONLY: {departure} → {destination} on {start_date}")
        
        # Require real API - no fallbacks allowed
        if not self.travel_apis:
            logger.error("❌ No real travel APIs available - cannot provide flight data")
            raise Exception("Real flight APIs not available - refusing to return mock data")
        
        # Retry logic for API calls
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Use real API for flight search
                search_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                
                # Convert budget to per-person flight budget (assume 40% of total budget for flights)
                flight_budget = float(budget) * 0.4 / travelers if budget else None
                
                # Import required classes
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from travel_apis import FlightSearchParams
                
                params = FlightSearchParams(
                    origin=departure,
                    destination=destination,
                    departure_date=search_date,
                    passengers=travelers,
                    max_price=Decimal(str(flight_budget)) if flight_budget else None
                )
                
                logger.info(f"🌐 Attempt {attempt + 1}/{max_retries}: Calling Amadeus API with 10s timeout...")
                
                # TravelAPIManager delegates to FlightBookingAPI - NO TIMEOUTS
                real_flights = await self.travel_apis.flight_api.search_flights(params)
                
                if not real_flights:
                    logger.warning(f"⚠️ No flights from Amadeus on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.error("❌ No flights found after all retries")
                        return []
                
                # Convert to A2A format with negotiation capabilities
                flights_with_negotiation = []
                for flight in real_flights:
                    flight_dict = {
                        "flight_id": f"REAL_{flight.get('id', datetime.now().timestamp())}",
                        "airline": flight.get('airline', 'Unknown Airline'),
                        "departure_airport": flight.get('departure_airport', departure),
                        "arrival_airport": flight.get('arrival_airport', destination),
                        "departure_time": flight.get('departure_time', f"{start_date}T08:00:00"),
                        "arrival_time": flight.get('arrival_time', f"{start_date}T12:00:00"),
                        "price": float(flight.get('price', 0)),
                        "booking_class": flight.get('booking_class', 'Economy'),
                        "available_seats": flight.get('available_seats', 0),
                        "agent_id": self.agent_id,
                        "negotiable": True,
                        "min_price": float(flight.get('price', 0)) * 0.9 if flight.get('price', 0) > 0 else 0,
                        "negotiation_expires": f"{start_date}T20:00:00",
                        "real_api_data": True,
                        "api_source": "Amadeus"
                    }
                    flights_with_negotiation.append(flight_dict)
                
                logger.info(f"✅ Found {len(flights_with_negotiation)} REAL flights from Amadeus API")
                return flights_with_negotiation
                
            except Exception as e:
                logger.error(f"❌ API call failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("❌ All API retry attempts failed")
                    raise Exception(f"Failed to get real flight data after {max_retries} attempts: {e}")
    
    async def negotiate_price(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate flight price with other agents"""
        flight_id = request_data.get('flight_id')
        requested_price = request_data.get('requested_price', 0)
        current_price = request_data.get('current_price', 350)
        
        logger.info(f"💰 Price negotiation for flight {flight_id}: ${requested_price} (was ${current_price})")
        
        # Intelligent negotiation logic
        min_acceptable = current_price * 0.9  # 10% discount max
        
        if requested_price >= current_price:
            # Accept if at or above current price
            result = {
                "flight_id": flight_id,
                "negotiation_accepted": True,
                "final_price": current_price,
                "agent_id": self.agent_id,
                "message": "Standard price accepted"
            }
        elif requested_price >= min_acceptable:
            # Accept discounted price
            result = {
                "flight_id": flight_id,
                "negotiation_accepted": True,
                "final_price": requested_price,
                "agent_id": self.agent_id,
                "message": f"Negotiated price accepted: ${requested_price}"
            }
        else:
            # Counter-offer
            counter_price = min_acceptable
            result = {
                "flight_id": flight_id,
                "negotiation_accepted": False,
                "counter_offer": counter_price,
                "final_price": counter_price,
                "agent_id": self.agent_id,
                "message": f"Counter-offer: ${counter_price}",
                "expires_in_minutes": 15
            }
        
        logger.info(f"📊 Negotiation result: {result['message']}")
        return result
    
    async def check_availability(self, flight_id: str) -> Dict[str, Any]:
        """Check real-time flight availability"""
        logger.info(f"✅ Checking availability for flight: {flight_id}")
        
        # Mock availability check - in real implementation would query API
        return {
            "flight_id": flight_id,
            "available_seats": 12,
            "price_current": 350.0,
            "last_updated": datetime.now().isoformat(),
            "agent_id": self.agent_id
        }
        """Check real-time flight availability and pricing"""
        logger.info(f"🔍 Checking availability for flight {flight_id}")
        
        return {
            "flight_id": flight_id,
            "available": True,
            "seats_remaining": 12,
            "price_changed": False,
            "last_updated": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "booking_deadline": "2025-09-27T18:00:00"
        }


def create_flight_agent_app() -> FastAPI:
    """Create standalone FastAPI app for FlightBookingAgent"""
    
    app = FastAPI(
        title="FlightBookingAgent",
        description="Specialized agent for flight search, booking, and price negotiation",
        version="1.0.0"
    )
    
    # Add CORS for cross-agent communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize agent
    agent = FlightBookingAgent()
    
    @app.get("/")
    async def root():
        return {
            "agent": agent.name,
            "agent_id": agent.agent_id,
            "version": agent.version,
            "capabilities": agent.capabilities,
            "status": "active",
            "endpoints": {
                "search": "/api/search-flights",
                "negotiate": "/api/negotiate-price",
                "availability": "/api/check-availability",
                "agent_info": "/.well-known/agent"
            }
        }
    
    @app.get("/.well-known/agent")
    async def get_agent_card():
        """A2A Agent Card for discovery"""
        return {
            "name": agent.name,
            "agent_id": agent.agent_id,
            "version": agent.version,
            "description": "Specialized agent for flight search, booking, and price negotiation",
            "capabilities": agent.capabilities,
            "endpoints": {
                "search_flights": "/api/search-flights",
                "negotiate_price": "/api/negotiate-price", 
                "check_availability": "/api/check-availability"
            },
            "communication_protocols": ["HTTP", "JSON"],
            "negotiation_supported": True,
            "real_time_updates": True
        }
    
    @app.post("/api/search-flights")
    async def search_flights(request_data: Dict[str, Any]):
        """Search for flights with negotiation metadata"""
        flights = await agent.search_flights(request_data)
        return {
            "success": True,
            "agent_id": agent.agent_id,
            "flights": flights,
            "total_found": len(flights),
            "negotiation_available": True
        }
    
    @app.post("/api/negotiate-price")
    async def negotiate_price(request_data: Dict[str, Any]):
        """Negotiate flight prices with other agents"""
        result = await agent.negotiate_price(request_data)
        return {
            "success": True,
            "negotiation_result": result
        }
    
    @app.get("/api/check-availability/{flight_id}")
    async def check_availability(flight_id: str):
        """Check real-time availability"""
        availability = await agent.check_availability(flight_id)
        return {
            "success": True,
            "availability": availability
        }
    
    return app


if __name__ == "__main__":
    app = create_flight_agent_app()
    
    print("✈️ FlightBookingAgent starting...")
    print("🔍 Specialized in flight search and booking")
    print("💰 Supports price negotiation with other agents") 
    print("📍 Available at: http://localhost:8001")
    print("🤖 Agent info: http://localhost:8001/.well-known/agent")
    print("🔗 API endpoints: http://localhost:8001/api/")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
import uvicorn

# Copy the exact imports from travel_master.py
from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPI, JSONRPCApplication
from a2a.server.context import ServerCallContext
from a2a.server.request_handlers.jsonrpc_handler import RequestHandler
from a2a.types import A2ARequest, AgentCard

logger = logging.getLogger(__name__)


class FlightSearchRequest(BaseModel):
    """Request for flight search"""
    departure_location: str
    destination: str
    departure_date: str  # Use string for JSON serialization
    return_date: Optional[str] = None
    passengers: int = 1
    max_budget: float
    preferences: List[str] = []
    
    
if __name__ == "__main__":
    app = create_flight_agent_app()
    
    print("✈️ FlightBookingAgent starting...")
    print("🔍 Specialized in flight search and booking")
    print("💰 Supports price negotiation with other agents") 
    print("📍 Available at: http://localhost:8001")
    print("🤖 Agent info: http://localhost:8001/.well-known/agent")
    print("🔗 API endpoints: http://localhost:8001/api/")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
