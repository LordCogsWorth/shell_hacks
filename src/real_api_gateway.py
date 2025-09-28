"""
TravelMaster API Gateway - Real API Integration
Direct integration with Amadeus, TripAdvisor, and Google Places APIs
"""

import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import logging
from datetime import datetime, date
from decimal import Decimal

# Import real API manager
try:
    from travel_apis import TravelAPIManager, FlightSearchParams, HotelSearchParams
    REAL_API_AVAILABLE = True
    print("✅ Real API integration available")
except ImportError as e:
    REAL_API_AVAILABLE = False
    print(f"⚠️ Real API not available: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize real API manager
travel_apis = None
if REAL_API_AVAILABLE:
    try:
        travel_apis = TravelAPIManager()
        print("✅ TravelAPIManager initialized with real APIs")
    except Exception as e:
        print(f"⚠️ TravelAPIManager init failed: {e}")
        travel_apis = None
else:
    print("⚠️ Using fallback mode without real APIs")

app = FastAPI(title="TravelMaster API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
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

# API Routes
@app.post("/api/plan-trip")
async def plan_trip(trip_request: TripRequest):
    """Plan a trip using REAL API integration"""
    try:
        print(f"🔍 Planning trip to {trip_request.destination} with REAL APIs")
        
        # Use real APIs directly if available
        if travel_apis and REAL_API_AVAILABLE:
            print("✅ Using REAL API integration for all services")
            
            # Convert dates
            start_date = datetime.strptime(trip_request.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(trip_request.end_date, '%Y-%m-%d').date()
            
            # Search all services with real APIs
            search_result = await travel_apis.search_all(
                destination=trip_request.destination,
                departure_location=trip_request.departure_location,
                start_date=start_date,
                end_date=end_date,
                travelers=trip_request.travelers,
                budget=Decimal(str(trip_request.budget)),
                preferences=trip_request.preferences
            )
            
            # Extract results from real API response
            flights = search_result.get("flights", [])
            hotels = search_result.get("hotels", [])
            activities = search_result.get("activities", [])
            # Handle restaurants - could be dict or list
            restaurants_data = search_result.get("restaurants", [])
            if isinstance(restaurants_data, dict):
                restaurants = restaurants_data.get("restaurants", [])
            else:
                restaurants = restaurants_data
            
            print(f"🛩️ Found {len(flights)} REAL flights from Amadeus")
            print(f"🏨 Found {len(hotels)} REAL hotels from Amadeus")
            print(f"🎯 Found {len(activities)} REAL activities from TripAdvisor/Google Places")
            print(f"🍽️ Found {len(restaurants)} REAL restaurants from Google Places")
            
        else:
            print("⚠️ Using enhanced mock data with real names")
            # Calculate nights for mock data
            nights = (datetime.strptime(trip_request.end_date, '%Y-%m-%d') - datetime.strptime(trip_request.start_date, '%Y-%m-%d')).days
            # Enhanced mock data with real airline/hotel names
            flights = [
                {
                    "flight_id": f"AA_{datetime.now().timestamp()}",
                    "airline": "American Airlines",
                    "departure_airport": trip_request.departure_location,
                    "arrival_airport": trip_request.destination,
                    "departure_time": f"{trip_request.start_date}T08:00:00",
                    "arrival_time": f"{trip_request.start_date}T14:30:00",
                    "price": 485,
                    "booking_class": "Economy",
                    "available_seats": 23,
                    "negotiable": True,
                    "min_price": 436.5,
                    "real_api_data": False
                },
                {
                    "flight_id": f"DL_{datetime.now().timestamp()}",
                    "airline": "Delta Air Lines", 
                    "departure_airport": trip_request.departure_location,
                    "arrival_airport": trip_request.destination,
                    "departure_time": f"{trip_request.start_date}T11:15:00",
                    "arrival_time": f"{trip_request.start_date}T17:45:00",
                    "price": 425,
                    "booking_class": "Economy",
                    "available_seats": 15,
                    "negotiable": True,
                    "min_price": 382.5,
                    "real_api_data": False
                }
            ]
            
            hotels = [
                {
                    "id": "marriott_001",
                    "name": "Marriott Downtown",
                    "rating": 4.5,
                    "price_per_night": 220,
                    "total_price": 220 * nights,
                    "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
                    "location": "City Center",
                    "review_score": 8.8,
                    "real_api_data": False
                },
                {
                    "id": "hilton_002", 
                    "name": "Hilton Garden Inn",
                    "rating": 4.2,
                    "price_per_night": 185,
                    "total_price": 185 * nights,
                    "amenities": ["WiFi", "Breakfast", "Fitness Center"],
                    "location": "Downtown",
                    "review_score": 8.3,
                    "real_api_data": False
                }
            ]
            
            activities = [
                {
                    "id": "museum_001",
                    "name": "Metropolitan Museum of Art",
                    "category": "museum",
                    "price": 25,
                    "rating": 4.8,
                    "duration": "3 hours",
                    "description": "World-famous art museum",
                    "real_api_data": False
                },
                {
                    "id": "tour_002",
                    "name": "City Walking Tour", 
                    "category": "tour",
                    "price": 35,
                    "rating": 4.6,
                    "duration": "2.5 hours",
                    "description": "Guided tour of historic landmarks",
                    "real_api_data": False
                },
                {
                    "id": "park_003",
                    "name": "Central Park",
                    "category": "outdoor",
                    "price": 0,
                    "rating": 4.7,
                    "duration": "2 hours",
                    "description": "Iconic urban park",
                    "real_api_data": False
                }
            ]
            
            restaurants = [
                {
                    "name": "Le Bernardin",
                    "rating": 4.9,
                    "cuisine_types": ["French", "Seafood"],
                    "estimated_cost": 85,
                    "price_level": 4,
                    "address": "Midtown West",
                    "real_api_data": False
                },
                {
                    "name": "Joe's Pizza",
                    "rating": 4.3,
                    "cuisine_types": ["Italian", "Pizza"],
                    "estimated_cost": 15,
                    "price_level": 1,
                    "address": "Greenwich Village",
                    "real_api_data": False
                }
            ]
        
        print(f"✅ Found {len(flights)} flights")
        print(f"✅ Found {len(hotels)} hotels")
        print(f"✅ Found {len(activities)} activities")
        
        # Calculate total cost (convert all to float to avoid Decimal/float errors)
        nights = (datetime.strptime(trip_request.end_date, '%Y-%m-%d') - datetime.strptime(trip_request.start_date, '%Y-%m-%d')).days
        flight_cost = float(min([f.get("price", 0) for f in flights])) if flights else 0.0
        hotel_cost = float(min([h.get("total_price", 0) for h in hotels])) if hotels else 0.0
        activity_cost = sum([float(a.get("price", 0)) for a in activities[:3]])  # Top 3 activities
        restaurant_cost = sum([float(r.get("estimated_cost", 0)) for r in restaurants[:2]]) * nights  # 2 meals per day
        
        total_cost = flight_cost + hotel_cost + activity_cost + restaurant_cost
        savings = float(trip_request.budget) - total_cost
        
        print(f"📊 Final results summary:")
        print(f"   • flights: {len(flights)} items")
        print(f"   • hotels: {len(hotels)} items")
        print(f"   • activities: {len(activities)} items")
        print(f"✅ Trip planned successfully - Total cost: ${total_cost:.2f}, Savings: ${savings:.2f}")
        
        return {
            "success": True,
            "request": trip_request.dict(),
            "flights": flights,
            "hotels": hotels,
            "activities": activities,
            "restaurants": restaurants,
            "total_cost": total_cost,
            "savings": savings,
            "start_date": trip_request.start_date,
            "end_date": trip_request.end_date,
            "agent_coordination": {
                "agents_used": ["flights", "hotels", "activities"],
                "coordination_time": datetime.now().isoformat(),
                "budget_optimization": True,
                "real_api_integration": REAL_API_AVAILABLE
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Trip planning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trip planning failed: {str(e)}")

@app.get("/api/agents/status")
async def agent_status():
    """Get status of all integrated services"""
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "real_api_integration": REAL_API_AVAILABLE,
        "services": {
            "flights": "Amadeus API" if REAL_API_AVAILABLE else "Enhanced Mock Data",
            "hotels": "Amadeus API" if REAL_API_AVAILABLE else "Enhanced Mock Data", 
            "activities": "TripAdvisor + Google Places" if REAL_API_AVAILABLE else "Enhanced Mock Data",
            "restaurants": "Google Places API" if REAL_API_AVAILABLE else "Enhanced Mock Data"
        },
        "endpoints": {
            "plan_trip": "/api/plan-trip",
            "generate_itinerary": "/api/generate-itinerary"
        }
    }

@app.post("/api/generate-itinerary")
async def generate_itinerary(itinerary_request: ItineraryRequest):
    """Generate a comprehensive itinerary"""
    trip_data = itinerary_request.trip_data
    
    # Simple itinerary generation
    itinerary = {
        "title": f"Your {trip_data.get('request', {}).get('destination', 'Dream')} Adventure",
        "duration": f"{trip_data.get('request', {}).get('start_date')} to {trip_data.get('request', {}).get('end_date')}",
        "summary": f"A wonderful trip for {trip_data.get('request', {}).get('travelers', 2)} travelers",
        "daily_schedule": [
            {
                "day": 1,
                "date": trip_data.get('request', {}).get('start_date'),
                "activities": ["Arrival", "Check-in", "Local exploration"]
            }
        ],
        "budget_breakdown": {
            "flights": trip_data.get('total_cost', 0) * 0.4,
            "hotels": trip_data.get('total_cost', 0) * 0.35,
            "activities": trip_data.get('total_cost', 0) * 0.15,
            "food": trip_data.get('total_cost', 0) * 0.10
        }
    }
    
    return {
        "success": True,
        "itinerary": itinerary,
        "generated_at": datetime.now().isoformat()
    }

# Frontend serving
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"✅ Frontend mounted from: {frontend_path}")
else:
    print(f"⚠️ Frontend directory not found at: {frontend_path}")

@app.get("/")
async def root():
    """Redirect to frontend"""
    return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    print("🚀 Starting TravelMaster API Gateway...")
    print("📡 Real API Integration:", "✅ Enabled" if REAL_API_AVAILABLE else "⚠️ Disabled")
    print("🌐 Frontend will be available at: http://localhost:8000/frontend/")
    print("📋 API status at: http://localhost:8000/api/agents/status")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
