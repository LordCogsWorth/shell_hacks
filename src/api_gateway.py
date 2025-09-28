#!/usr/bin/env python3
"""
API Gateway for TravelMaster Frontend
Connects the React frontend to distributed A2A agents
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
import uvicorn
from pathlib import Path
import logging

# Try to import real APIs
try:
    from travel_apis import TravelAPIManager, FlightSearchParams, HotelSearchParams
    REAL_API_AVAILABLE = True
    print("✅ Real API integration available")
except ImportError as e:
    REAL_API_AVAILABLE = False
    TravelAPIManager = None
    print(f"⚠️ Real API not available: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize real API manager
travel_apis = None
if REAL_API_AVAILABLE and TravelAPIManager:
    travel_apis = TravelAPIManager()
    print("✅ TravelAPIManager initialized with real APIs")
else:
    print("⚠️ Using fallback mode without real APIs")

app = FastAPI(title="TravelMaster API Gateway", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A2A Agent endpoints
AGENTS = {
    "flight": "http://localhost:8001",
    "hotel": "http://localhost:8002",
    "activity": "http://localhost:8003", 
    "gemini": "http://localhost:8004",
    "discovery": "http://localhost:8005"
}

# Pydantic models
class TripRequest(BaseModel):
    destination: str
    departure_location: str
    start_date: str
    end_date: str
    budget: float
    travelers: int = 2
    preferences: List[str] = []
    special_requirements: str = ""

class ItineraryRequest(BaseModel):
    trip_data: Dict[str, Any]
    special_instructions: str = "Create a memorable travel experience"

# Helper functions
async def call_agent(agent_url: str, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Call an A2A agent endpoint"""
    full_url = f"{agent_url}/{endpoint}"
    try:
        print(f"🌐 Calling: {full_url}")
        print(f"📤 Request data: {data}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(full_url, json=data)
            print(f"📨 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success response: {result}")
                return result
            else:
                print(f"❌ Agent {agent_url} returned {response.status_code}: {response.text}")
                return None
    except Exception as e:
        print(f"💥 Error calling agent {agent_url}: {e}")
        return None

async def discover_agents() -> List[Dict[str, Any]]:
    """Get list of available agents from discovery service"""
    try:
        discovery_data = await call_agent(AGENTS["discovery"], "discover_all_agents", {})
        if discovery_data and "agents" in discovery_data:
            return discovery_data["agents"]
        return []
    except Exception as e:
        print(f"Error discovering agents: {e}")
        return []

# API Routes
@app.post("/api/plan-trip")
async def plan_trip(trip_request: TripRequest):
    """Plan a trip using distributed A2A agents"""
    try:
        # Convert request to agent format
        request_data = {
            "destination": trip_request.destination,
            "departure_location": trip_request.departure_location,
            "start_date": trip_request.start_date,
            "end_date": trip_request.end_date,
            "budget": trip_request.budget,
            "travelers": trip_request.travelers,
            "preferences": trip_request.preferences,
            "special_requirements": trip_request.special_requirements
        }
        
        # Discover available agents
        available_agents = await discover_agents()
        print(f"🔍 Discovered {len(available_agents)} agents")
        
        # Parallel agent calls for better performance
        tasks = []
        
        print(f"🔍 Starting agent coordination for trip to {request_data['destination']}")
        
        # Flight search
        print(f"🛩️ Calling Flight Agent at {AGENTS['flight']}")
        flight_task = asyncio.create_task(
            call_agent(AGENTS["flight"], "api/search-flights", request_data)
        )
        tasks.append(("flights", flight_task))
        
        # Hotel search  
        print(f"🏨 Calling Hotel Agent at {AGENTS['hotel']}")
        hotel_task = asyncio.create_task(
            call_agent(AGENTS["hotel"], "api/search-hotels", request_data)
        )
        tasks.append(("hotels", hotel_task))
        
        # Activity search
        print(f"🎯 Calling Activity Agent at {AGENTS['activity']}")
        activity_task = asyncio.create_task(
            call_agent(AGENTS["activity"], "api/search-activities", request_data)
        )
        tasks.append(("activities", activity_task))
        
        # Wait for all agent responses
        results = {}
        for name, task in tasks:
            print(f"⏳ Waiting for {name} agent response...")
            result = await task
            print(f"📥 {name.title()} agent response: {result}")
            
            if result and result.get("success", False):
                # Extract data from agent response based on agent type
                if name == "flights" and "flights" in result:
                    results[name] = result["flights"]
                    print(f"✅ Found {len(result['flights'])} flights")
                elif name == "hotels" and "hotels" in result:
                    results[name] = result["hotels"]
                    print(f"✅ Found {len(result['hotels'])} hotels")
                elif name == "activities" and "activities" in result:
                    results[name] = result["activities"]
                    print(f"✅ Found {len(result['activities'])} activities")
                elif "results" in result:
                    results[name] = result["results"]
                    print(f"✅ Found {len(result['results'])} {name}")
                else:
                    # If it's a list directly, use it
                    if isinstance(result, list):
                        results[name] = result
                        print(f"✅ Found {len(result)} {name} (direct list)")
                    else:
                        results[name] = []
                        print(f"⚠️ Unexpected response format from {name}: {result}")
            else:
                results[name] = []
                print(f"❌ No valid result from {name} agent")
        
        print(f"📊 Final results summary:")
        for name, data in results.items():
            print(f"   • {name}: {len(data)} items")
        
        # Calculate total cost and savings
        total_cost = 0
        
        # Calculate flight costs
        if results["flights"]:
            flight_cost = sum(flight.get("price", 0) for flight in results["flights"][:2])  # Outbound + return
            total_cost += flight_cost * trip_request.travelers
        
        # Calculate hotel costs
        if results["hotels"]:
            hotel = results["hotels"][0]
            days = (datetime.fromisoformat(trip_request.end_date) - datetime.fromisoformat(trip_request.start_date)).days
            hotel_cost = hotel.get("price_per_night", 0) * days
            total_cost += hotel_cost
        
        # Calculate activity costs
        if results["activities"]:
            activity_cost = sum(activity.get("price", 0) for activity in results["activities"][:3])
            total_cost += activity_cost * trip_request.travelers
        
        # Calculate restaurant costs (estimate)
        restaurant_cost = 75 * trip_request.travelers * max(1, (datetime.fromisoformat(trip_request.end_date) - datetime.fromisoformat(trip_request.start_date)).days)
        total_cost += restaurant_cost
        
        savings = max(0, trip_request.budget - total_cost)
        
        # Generate sample restaurants (since we don't have a restaurant agent yet)
        sample_restaurants = [
            {
                "name": f"Local Bistro {i+1}",
                "rating": 4.2 + (i * 0.3),
                "address": f"Downtown {trip_request.destination}",
                "cuisine_types": ["Local", "International"],
                "estimated_cost": 35 + (i * 15),
                "price_level": 2 + i,
                "phone": f"+1-555-{1000 + i*100}",
                "opening_hours": ["11:00 AM - 10:00 PM"]
            }
            for i in range(3)
        ]
        
        # Construct response in expected frontend format
        response = {
            "request": request_data,
            "flights": results["flights"][:2],  # Limit to 2 flights
            "hotels": results["hotels"][:1],    # Limit to 1 hotel
            "activities": results["activities"][:4],  # Limit to 4 activities
            "restaurants": sample_restaurants,
            "total_cost": total_cost,
            "savings": savings,
            "start_date": trip_request.start_date,
            "end_date": trip_request.end_date,
            "success": True,
            "agent_coordination": {
                "agents_used": list(results.keys()),
                "coordination_time": datetime.now().isoformat(),
                "budget_optimization": True
            }
        }
        
        print(f"✅ Trip planned successfully - Total cost: ${total_cost:.2f}, Savings: ${savings:.2f}")
        return response
        
    except Exception as e:
        print(f"❌ Error planning trip: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to plan trip: {str(e)}")

@app.post("/api/generate-itinerary")
async def generate_comprehensive_itinerary(itinerary_request: ItineraryRequest):
    """Generate comprehensive AI itinerary using Gemini agent"""
    try:
        # Call Gemini AI agent for comprehensive itinerary
        gemini_data = {
            "trip_data": itinerary_request.trip_data,
            "special_instructions": itinerary_request.special_instructions
        }
        
        result = await call_agent(AGENTS["gemini"], "generate_comprehensive_itinerary", gemini_data)
        
        if result:
            print(f"✅ Comprehensive itinerary generated with {result.get('confidence_score', 'N/A')}% confidence")
            return result
        else:
            # Fallback response if Gemini agent is unavailable
            print("⚠️ Gemini agent unavailable, providing fallback itinerary")
            return {
                "comprehensive_plan": "AI-enhanced itinerary will be generated once Gemini agent is available.",
                "daily_schedule": itinerary_request.trip_data.get("activities", []),
                "smart_recommendations": ["Budget optimized", "Time efficient routes", "Local experiences included"],
                "confidence_score": 85,
                "ai_insights": "Fallback mode - limited AI features available",
                "status": "generated_fallback"
            }
            
    except Exception as e:
        print(f"❌ Error generating itinerary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate itinerary: {str(e)}")

@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all A2A agents"""
    try:
        available_agents = await discover_agents()
        
        # Test connectivity to each agent using their .well-known/agent endpoint
        agent_status = {}
        for agent_name, agent_url in AGENTS.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{agent_url}/.well-known/agent", timeout=5.0)
                    agent_status[agent_name] = {
                        "url": agent_url,
                        "status": "online" if response.status_code == 200 else "error",
                        "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None,
                        "info": response.json() if response.status_code == 200 else None
                    }
            except Exception as e:
                agent_status[agent_name] = {
                    "url": agent_url,
                    "status": "offline",
                    "error": str(e)
                }
        
        return {
            "agents": agent_status,
            "discovered_agents": available_agents,
            "total_agents": len(AGENTS),
            "online_agents": len([a for a in agent_status.values() if a["status"] == "online"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/api/calendar/{trip_id}")
async def get_calendar_data(trip_id: str):
    """Get calendar data for a trip (sample implementation)"""
    # This is a placeholder - you can enhance with real trip data
    return {
        "trip_id": trip_id,
        "events": [
            {
                "summary": "Flight Departure",
                "start": "2025-10-27T08:00:00Z",
                "end": "2025-10-27T10:00:00Z",
                "location": "Airport"
            }
        ]
    }

@app.post("/api/monitor-disruptions")
async def monitor_disruptions(request: Request):
    """Setup disruption monitoring (sample implementation)"""
    data = await request.json()
    return {
        "monitoring_id": f"MON_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "active",
        "trip_id": data.get("trip_id"),
        "notifications": data.get("notifications", [])
    }

# Serve frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend"  # Go up one level to find frontend
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    print(f"✅ Frontend mounted from: {frontend_dir.absolute()}")
else:
    print(f"❌ Frontend directory not found at: {frontend_dir.absolute()}")

@app.get("/")
async def root():
    """Redirect to frontend"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"message": "TravelMaster API Gateway", "agents": list(AGENTS.keys()), "frontend_available": frontend_dir.exists()}

if __name__ == "__main__":
    print("🚀 Starting TravelMaster API Gateway...")
    print("📡 Connecting to A2A agents:")
    for name, url in AGENTS.items():
        print(f"   • {name.title()} Agent: {url}")
    print("🌐 Frontend will be available at: http://localhost:8000/frontend/")
    print("📋 API status at: http://localhost:8000/api/agents/status")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
