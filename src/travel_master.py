"""
TravelMaster AI Agent - Core Application Architecture

This module defines the main travel planning agent that coordinates
all travel-related services using the A2A protocol.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass, asdict
from enum import Enum
from pydantic import BaseModel

from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPI, JSONRPCApplication
from a2a.server.context import ServerCallContext
from a2a.server.request_handlers.jsonrpc_handler import RequestHandler
from a2a.types import A2ARequest, AgentCard

logger = logging.getLogger(__name__)


class TravelPreferences(Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range" 
    LUXURY = "luxury"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CULTURAL = "cultural"


@dataclass
class TravelRequest:
    """Represents a complete travel planning request"""
    destination: str
    departure_location: str
    start_date: date
    end_date: date
    budget: Decimal
    travelers: int
    preferences: List[TravelPreferences]
    special_requirements: Optional[str] = None
    

@dataclass
class TravelItinerary:
    """Complete travel itinerary with all bookings"""
    request: TravelRequest
    flights: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    total_cost: Decimal
    daily_schedule: List[Dict[str, Any]]
    budget_breakdown: Dict[str, Decimal]


class TravelMasterAgent:
    """
    Main AI Travel Agent that coordinates all travel planning services
    using the A2A protocol for microservice communication.
    """
    
    def __init__(self):
        self.flight_agent = None  # Will connect to flight booking service
        self.hotel_agent = None   # Will connect to hotel booking service
        self.activity_agent = None # Will connect to activity booking service
        self.budget_agent = None  # Will connect to budget management service
        
    async def plan_trip(self, request: TravelRequest) -> TravelItinerary:
        """
        Main entry point for travel planning.
        Coordinates with all sub-agents to create complete itinerary.
        """
        # Step 1: Get flight options within budget
        flights = await self._get_flight_options(request)
        
        # Step 2: Find hotels based on remaining budget
        remaining_budget = request.budget - sum(f['price'] for f in flights)
        hotels = await self._get_hotel_options(request, remaining_budget)
        
        # Step 3: Plan activities with remaining budget
        activity_budget = remaining_budget - sum(h['price'] for h in hotels)
        activities = await self._get_activity_options(request, activity_budget)
        
        # Step 4: Create optimized daily schedule
        schedule = await self._create_daily_schedule(request, hotels, activities)
        
        # Step 5: Calculate final costs and budget breakdown
        total_cost, breakdown = await self._calculate_costs(flights, hotels, activities)
        
        return TravelItinerary(
            request=request,
            flights=flights,
            hotels=hotels,
            activities=activities,
            total_cost=total_cost,
            daily_schedule=schedule,
            budget_breakdown=breakdown
        )
    
    async def _get_flight_options(self, request: TravelRequest) -> List[Dict[str, Any]]:
        """Get flight options from flight booking agent"""
        # TODO: Implement A2A communication with flight service
        return []
    
    async def _get_hotel_options(self, request: TravelRequest, budget: Decimal) -> List[Dict[str, Any]]:
        """Get hotel options from hotel booking agent"""
        # TODO: Implement A2A communication with hotel service
        return []
    
    async def _get_activity_options(self, request: TravelRequest, budget: Decimal) -> List[Dict[str, Any]]:
        """Get activity options from activity booking agent"""
        # TODO: Implement A2A communication with activity service
        return []
    
    async def _create_daily_schedule(self, request: TravelRequest, hotels: List, activities: List) -> List[Dict[str, Any]]:
        """Create optimized daily schedule"""
        # TODO: Implement intelligent scheduling algorithm
        return []
    
    async def _calculate_costs(self, flights: List, hotels: List, activities: List) -> tuple[Decimal, Dict[str, Decimal]]:
        """Calculate total costs and budget breakdown"""
        # TODO: Implement cost calculation
        return Decimal("0"), {}


class TravelPlanningHandler(RequestHandler):
    """A2A Request Handler for Travel Planning"""
    
    def __init__(self):
        super().__init__()
        self.agent = TravelMasterAgent()
    
    async def plan_trip(self, context: ServerCallContext, request: A2ARequest) -> Dict[str, Any]:
        """Handle travel planning requests"""
        try:
            # Extract travel parameters from request
            params = request.params or {}
            
            travel_request = TravelRequest(
                destination=params.get("destination", ""),
                departure_location=params.get("departure_location", ""),
                start_date=datetime.fromisoformat(params.get("start_date", "")).date(),
                end_date=datetime.fromisoformat(params.get("end_date", "")).date(),
                budget=Decimal(str(params.get("budget", "0"))),
                travelers=int(params.get("travelers", 1)),
                preferences=[TravelPreferences(p) for p in params.get("preferences", [])],
                special_requirements=params.get("special_requirements")
            )
            
            # Plan the trip
            itinerary = await self.agent.plan_trip(travel_request)
            
            return {
                "success": True,
                "itinerary": asdict(itinerary),
                "message": "Travel itinerary created successfully! 🌍✈️"
            }
            
        except Exception as e:
            logger.error(f"Failed to create travel itinerary: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create travel itinerary. Please check your request and try again."
            }


def create_travel_master_app() -> A2AFastAPI:
    """Create the TravelMaster FastAPI application"""
    
    # Create the FastAPI app with A2A extensions
    app = A2AFastAPI(
        title="TravelMaster AI Agent",
        description="AI-powered travel planning agent using Agent2Agent protocol",
        version="1.0.0"
    )
    
    # Create the JSON-RPC application
    handler = TravelPlanningHandler()
    rpc_app = JSONRPCApplication(handler)
    
    # Add agent card endpoint
    agent_card = AgentCard(
        name="TravelMaster",
        description="AI travel planning agent that books flights, hotels, and activities while staying within budget",
        version="1.0.0",
        capabilities=[
            "flight_booking",
            "hotel_booking", 
            "activity_planning",
            "budget_management",
            "itinerary_generation"
        ]
    )
    
    @app.get("/.well-known/agent")
    async def get_agent_card():
        return agent_card.model_dump()
    
    # Mount the JSON-RPC endpoint
    app.mount("/rpc", rpc_app)
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    # Create and run the TravelMaster app
    app = create_travel_master_app()
    
    print("🌍 TravelMaster AI Agent starting...")
    print("Ready to plan your dream vacation!")
    print("Available at: http://localhost:8000")
    print("Agent card: http://localhost:8000/.well-known/agent")
    print("RPC endpoint: http://localhost:8000/rpc")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
