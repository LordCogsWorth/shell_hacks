"""
TravelMaster AI Agent - Simplified Implementation

A basic travel planning service that will be enhanced with A2A protocol integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import asyncio
import uvicorn


class TravelPreferences(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range" 
    LUXURY = "luxury"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CULTURAL = "cultural"


class TravelRequest(BaseModel):
    destination: str = Field(..., description="Destination city/country")
    departure_location: str = Field(..., description="Departure city/airport")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    budget: Decimal = Field(..., description="Total budget in USD", gt=0)
    travelers: int = Field(..., description="Number of travelers", gt=0)
    preferences: List[TravelPreferences] = Field(default=[], description="Travel preferences")
    special_requirements: Optional[str] = Field(None, description="Special requirements or requests")


class FlightOption(BaseModel):
    airline: str
    departure_time: datetime
    arrival_time: datetime
    price: Decimal
    stops: int = 0
    duration: str


class HotelOption(BaseModel):
    name: str
    rating: float
    price_per_night: Decimal
    total_price: Decimal
    location: str
    amenities: List[str]


class ActivityOption(BaseModel):
    name: str
    type: str
    description: str
    price: Decimal
    duration: str
    location: str
    rating: float


class TravelItinerary(BaseModel):
    request: TravelRequest
    flights: List[FlightOption]
    hotels: List[HotelOption]
    activities: List[ActivityOption]
    total_cost: Decimal
    savings: Decimal
    daily_schedule: List[Dict[str, Any]]
    budget_breakdown: Dict[str, Decimal]


class TravelPlanningService:
    """Core travel planning service"""
    
    def __init__(self):
        # Import here to avoid circular imports
        from travel_apis import travel_apis
        self.travel_apis = travel_apis
    
    async def plan_trip(self, request: TravelRequest) -> TravelItinerary:
        """Main trip planning orchestrator using real APIs"""
        
        # Search all travel options simultaneously using external APIs
        search_results = await self.travel_apis.search_all(
            destination=request.destination,
            departure_location=request.departure_location,
            start_date=request.start_date,
            end_date=request.end_date,
            travelers=request.travelers,
            budget=request.budget,
            preferences=[pref.value for pref in request.preferences]
        )
        
        # Convert API results to our models
        flights = [FlightOption(
            airline=f["airline"],
            departure_time=f["departure_time"],
            arrival_time=f["arrival_time"], 
            price=f["price"],
            stops=f["stops"],
            duration=f["duration"]
        ) for f in search_results["flights"][:2]]  # Take top 2 flights
        
        hotels = [HotelOption(
            name=h["name"],
            rating=h["rating"],
            price_per_night=h["price_per_night"],
            total_price=h["total_price"],
            location=h["location"],
            amenities=h["amenities"]
        ) for h in search_results["hotels"][:3]]  # Take top 3 hotels
        
        activities = [ActivityOption(
            name=a["name"],
            type=a["category"],
            description=a["description"],
            price=a["price"],
            duration=a["duration"],
            location=a.get("meeting_point", request.destination),
            rating=a["rating"]
        ) for a in search_results["activities"][:5]]  # Take top 5 activities
        
        # Create daily schedule
        daily_schedule = await self._create_daily_schedule(request, hotels, activities)
        
        # Calculate costs
        total_cost = sum([f.price for f in flights] + 
                        [h.total_price for h in hotels] + 
                        [a.price for a in activities[:3]])  # Limit to 3 activities
        
        savings = request.budget - total_cost
        
        budget_breakdown = {
            "flights": sum(f.price for f in flights),
            "hotels": sum(h.total_price for h in hotels),
            "activities": sum(a.price for a in activities[:3]),
            "remaining": savings
        }
        
        return TravelItinerary(
            request=request,
            flights=flights,
            hotels=hotels,
            activities=activities[:3],  # Limit activities in final itinerary
            total_cost=total_cost,
            savings=savings,
            daily_schedule=daily_schedule,
            budget_breakdown=budget_breakdown
        )
    
    async def _find_flights(self, request: TravelRequest, budget: Decimal) -> List[FlightOption]:
        """Find flight options within budget"""
        # Mock flight data - replace with real API calls
        await asyncio.sleep(0.1)  # Simulate API call
        
        return [
            FlightOption(
                airline="American Airlines",
                departure_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=8)),
                arrival_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=14)),
                price=min(budget * Decimal("0.8"), Decimal("450")),
                stops=0,
                duration="6h 30m"
            ),
            FlightOption(
                airline="Delta",
                departure_time=datetime.combine(request.end_date, datetime.min.time().replace(hour=16)),
                arrival_time=datetime.combine(request.end_date, datetime.min.time().replace(hour=22)),
                price=min(budget * Decimal("0.2"), Decimal("380")),
                stops=1,
                duration="8h 15m"
            )
        ]
    
    async def _find_hotels(self, request: TravelRequest, budget: Decimal) -> List[HotelOption]:
        """Find hotel options within budget"""
        # Mock hotel data - replace with real API calls
        await asyncio.sleep(0.1)  # Simulate API call
        
        nights = (request.end_date - request.start_date).days
        price_per_night = budget / nights if nights > 0 else budget
        
        return [
            HotelOption(
                name="Downtown Hotel",
                rating=4.2,
                price_per_night=price_per_night * Decimal("0.8"),
                total_price=price_per_night * Decimal("0.8") * nights,
                location="City Center",
                amenities=["WiFi", "Pool", "Gym", "Restaurant"]
            )
        ]
    
    async def _find_activities(self, request: TravelRequest, budget: Decimal) -> List[ActivityOption]:
        """Find activity options within budget"""
        # Mock activity data - replace with real API calls
        await asyncio.sleep(0.1)  # Simulate API call
        
        return [
            ActivityOption(
                name="City Walking Tour",
                type="sightseeing",
                description="Explore the historic city center with a local guide",
                price=budget * Decimal("0.3"),
                duration="3 hours",
                location="City Center",
                rating=4.5
            ),
            ActivityOption(
                name="Local Food Experience",
                type="culinary",
                description="Taste authentic local cuisine with a food expert",
                price=budget * Decimal("0.4"),
                duration="2.5 hours", 
                location="Food District",
                rating=4.8
            )
        ]
    
    async def _create_daily_schedule(self, request: TravelRequest, hotels: List[HotelOption], activities: List[ActivityOption]) -> List[Dict[str, Any]]:
        """Create an optimized daily schedule"""
        schedule = []
        current_date = request.start_date
        
        while current_date <= request.end_date:
            day_activities = []
            
            if current_date == request.start_date:
                day_activities.append({
                    "time": "08:00",
                    "activity": "Departure Flight",
                    "type": "travel"
                })
                day_activities.append({
                    "time": "15:00", 
                    "activity": "Hotel Check-in",
                    "type": "accommodation"
                })
            
            if len(activities) > 0 and current_date != request.start_date and current_date != request.end_date:
                for i, activity in enumerate(activities[:2]):  # Limit to 2 activities per day
                    day_activities.append({
                        "time": f"{10 + i*3:02d}:00",
                        "activity": activity.name,
                        "type": activity.type,
                        "duration": activity.duration,
                        "price": float(activity.price)
                    })
            
            if current_date == request.end_date:
                day_activities.append({
                    "time": "12:00",
                    "activity": "Hotel Check-out", 
                    "type": "accommodation"
                })
                day_activities.append({
                    "time": "16:00",
                    "activity": "Return Flight",
                    "type": "travel"
                })
            
            schedule.append({
                "date": current_date.isoformat(),
                "activities": day_activities
            })
            
            current_date = date.fromordinal(current_date.toordinal() + 1)
        
        return schedule


# Create FastAPI app
app = FastAPI(
    title="TravelMaster AI Agent",
    description="AI-powered travel planning service that creates complete itineraries within your budget",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Mount static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Initialize the travel service
travel_service = TravelPlanningService()


@app.post("/api/plan-trip", response_model=TravelItinerary)
async def plan_trip(request: TravelRequest):
    """Plan a complete trip based on user requirements"""
    try:
        itinerary = await travel_service.plan_trip(request)
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to plan trip: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TravelMaster AI Agent"}


@app.get("/")
async def root():
    """Serve the frontend application"""
    frontend_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        return {
            "service": "TravelMaster AI Agent",
            "description": "AI-powered travel planning service",
            "version": "1.0.0",
            "endpoints": {
                "plan_trip": "/api/plan-trip",
                "health": "/api/health",
                "docs": "/docs"
            }
        }

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "service": "TravelMaster AI Agent",
        "description": "AI-powered travel planning service with voice interaction",
        "version": "1.0.0",
        "features": [
            "AI-powered trip planning",
            "Voice interaction",
            "Budget optimization", 
            "Real-time booking",
            "Multi-preference support"
        ],
        "endpoints": {
            "plan_trip": "/api/plan-trip",
            "health": "/api/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    print("🌍 TravelMaster AI Agent starting...")
    print("🚀 Ready to plan your dream vacation!")
    print("📍 Server running at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)