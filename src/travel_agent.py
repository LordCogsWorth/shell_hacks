"""
TravelMaster AI Agent - Simplified Implementation

A basic travel planning service that will be enhanced with A2A protocol integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
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
    flight_id: str
    airline: str
    aircraft: Optional[str]
    departure_time: datetime
    arrival_time: datetime
    departure_airport: str
    arrival_airport: str
    price: Decimal
    stops: int = 0
    duration: str
    travel_class: str
    available_seats: str
    instant_confirmation: bool = True


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


class RestaurantOption(BaseModel):
    id: str
    name: str
    rating: float
    price_level: int  # 0-4 scale from Google Places
    address: str
    cuisine_types: List[str]
    estimated_cost: Decimal
    reviews_count: int
    phone: Optional[str] = ""
    website: Optional[str] = ""
    opening_hours: List[str] = []
    specialties: List[str] = []


class TravelItinerary(BaseModel):
    request: TravelRequest
    flights: List[FlightOption]
    hotels: List[HotelOption]
    activities: List[ActivityOption]
    restaurants: List[RestaurantOption]  # ← NEW
    total_cost: Decimal
    savings: Decimal
    daily_schedule: List[Dict[str, Any]]
    budget_breakdown: Dict[str, Decimal]


class TravelPlanningService:
    """Core travel planning service"""
    
    def __init__(self):
        # Import here to avoid circular imports
        try:
            from .travel_apis import travel_apis
        except ImportError:
            from travel_apis import travel_apis
        self.travel_apis = travel_apis
    
    async def plan_trip(self, request: TravelRequest) -> TravelItinerary:
        """Plan a complete trip based on user requirements using real APIs"""
        
        print(f"🌍 Planning trip to {request.destination} for {request.travelers} travelers")
        print(f"💰 Budget: ${request.budget}, Dates: {request.start_date} to {request.end_date}")
        
        # Validate dates
        if request.end_date <= request.start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Use the TravelAPIManager to search all services
        try:
            api_results = await self.travel_apis.search_all(
                destination=request.destination,
                departure_location=request.departure_location,
                start_date=request.start_date,
                end_date=request.end_date,
                travelers=request.travelers,
                budget=request.budget,
                preferences=[pref.value for pref in request.preferences]
            )
            
            # Convert API results to Pydantic models
            flights = []
            if api_results.get("flights"):
                for flight_data in api_results["flights"][:2]:  # Take first 2 flights
                    # Build full FlightOption from API fields
                    departure_str = flight_data.get("departure_time", "")
                    arrival_str = flight_data.get("arrival_time", "")
                    try:
                        departure_time = datetime.fromisoformat(departure_str.replace('Z', '+00:00')) if departure_str else datetime.combine(request.start_date, datetime.min.time().replace(hour=8))
                    except:
                        departure_time = datetime.combine(request.start_date, datetime.min.time().replace(hour=8))
                    try:
                        arrival_time = datetime.fromisoformat(arrival_str.replace('Z', '+00:00')) if arrival_str else datetime.combine(request.start_date, datetime.min.time().replace(hour=14))
                    except:
                        arrival_time = datetime.combine(request.start_date, datetime.min.time().replace(hour=14))

                    try:
                        flight_option = FlightOption(
                            flight_id=flight_data.get("id", "unknown"),
                            airline=flight_data.get("airline", "Unknown"),
                            aircraft=flight_data.get("aircraft"),
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            departure_airport=flight_data.get("departure_airport", ""),
                            arrival_airport=flight_data.get("arrival_airport", ""),
                            price=Decimal(str(flight_data.get("price", 500))),
                            stops=flight_data.get("stops", 0),
                            duration=flight_data.get("duration", "6h 00m"),
                            travel_class=flight_data.get("class", "Economy"),
                            available_seats=f"{flight_data.get('available_seats', 0)} seats available",
                            instant_confirmation=bool(flight_data.get("instant_confirmation", True))
                        )
                        flights.append(flight_option)
                        print(f"✅ Created FlightOption: {flight_option.airline}")
                    except Exception as flight_error:
                        print(f"❌ Error creating FlightOption: {flight_error}")
                        print(f"   Flight data: {flight_data}")
                        continue
            
            # Convert hotel API results
            hotels = []
            if api_results.get("hotels"):
                for hotel_data in api_results["hotels"][:1]:  # Take first hotel
                    hotels.append(HotelOption(
                        name=hotel_data.get("name", "Hotel"),
                        rating=float(hotel_data.get("rating", 4.0)),
                        price_per_night=Decimal(str(hotel_data.get("price_per_night", 120))),
                        total_price=Decimal(str(hotel_data.get("total_price", 600))),
                        location=hotel_data.get("location", "City Center"),
                        amenities=hotel_data.get("amenities", ["WiFi"])
                    ))
            
            # Convert activity API results - show sights to see and things to do
            activities = []
            if api_results.get("activities"):
                # Separate sights vs activities
                sights = []
                experiences = []
                
                for activity_data in api_results["activities"][:8]:  # Process up to 8 items
                    activity = ActivityOption(
                        name=activity_data.get("name", "Activity"),
                        type=activity_data.get("type", "sightseeing"),
                        description=activity_data.get("description", "Fun activity"),
                        price=Decimal(str(activity_data.get("price", 50))),
                        duration=activity_data.get("duration", "2 hours"),
                        location=activity_data.get("location", "City Center"),
                        rating=float(activity_data.get("rating", 4.0))
                    )
                    activities.append(activity)
                    
                    # Categorize as sight vs activity (check both type and category fields)
                    activity_type = activity_data.get("type", "")
                    activity_category = activity_data.get("category", "")
                    combined_type = f"{activity_type} {activity_category}".lower()
                    
                    if any(word in combined_type for word in ["sight", "landmark", "viewpoint", "district", "architectural"]):
                        sights.append(activity)
                    else:
                        experiences.append(activity)
                
                # Display organized results
                print(f"🎯 AI Agent found {len(sights)} sights to see and {len(experiences)} activities to do:")
                
                if sights:
                    print("   👁️  SIGHTS TO SEE:")
                    for i, sight in enumerate(sights[:4], 1):
                        price_text = f"${sight.price}" if sight.price > 0 else "Free"
                        print(f"      {i}. {sight.name} - {price_text} ({sight.duration})")
                
                if experiences:
                    print("   🎪 ACTIVITIES TO DO:")
                    for i, exp in enumerate(experiences[:4], 1):
                        print(f"      {i}. {exp.name} - ${exp.price} ({exp.duration})")
                    
        except Exception as e:
            print(f"❌ Error using travel APIs: {e}")
            print("🔄 Falling back to mock data")
            
            # Fallback to mock data if APIs fail
            flights = [
                FlightOption(
                    flight_id="mock_flight_001",
                    airline="American Airlines",
                    aircraft="Boeing 737-800",
                    departure_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=8)),
                    arrival_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=14)),
                    departure_airport=request.departure_location[:3].upper(),
                    arrival_airport=request.destination[:3].upper(),
                    price=min(request.budget * Decimal("0.4"), Decimal("600")),
                    stops=0,
                    duration="6h 30m",
                    travel_class="Economy",
                    available_seats="15 seats available",
                    instant_confirmation=True
                ),
                FlightOption(
                    flight_id="mock_flight_002",
                    airline="Delta",
                    aircraft="Airbus A320",
                    departure_time=datetime.combine(request.end_date, datetime.min.time().replace(hour=16)),
                    arrival_time=datetime.combine(request.end_date, datetime.min.time().replace(hour=22)),
                    departure_airport=request.destination[:3].upper(),
                    arrival_airport=request.departure_location[:3].upper(),
                    price=min(request.budget * Decimal("0.3"), Decimal("500")),
                    stops=1,
                    duration="8h 15m",
                    travel_class="Economy",
                    available_seats="8 seats available",
                    instant_confirmation=True
                )
            ]
            
            nights = (request.end_date - request.start_date).days
            price_per_night = min(request.budget * Decimal("0.2") / nights if nights > 0 else request.budget * Decimal("0.2"), Decimal("200"))
            
            hotels = [
                HotelOption(
                    name="Downtown Hotel",
                    rating=4.2,
                    price_per_night=price_per_night,
                    total_price=price_per_night * nights,
                    location="City Center",
                    amenities=["WiFi", "Pool", "Gym", "Restaurant"]
                )
            ]
            
            activities = [
                ActivityOption(
                    name="City Tour",
                    type="sightseeing",
                    description="Guided city tour with local guide",
                    price=min(request.budget * Decimal("0.05"), Decimal("80")),
                    duration="3 hours",
                    location="City Center",
                    rating=4.5
                ),
                ActivityOption(
                    name="Museum Visit",
                    type="cultural",
                    description="Visit to local art museum",
                    price=min(request.budget * Decimal("0.03"), Decimal("45")),
                    duration="2 hours",
                    location="Arts District", 
                    rating=4.3
                )
            ]
        
        # Search for restaurants within budget
        try:
            restaurant_results = await self.travel_apis.search_restaurants(
                destination=request.destination,
                max_budget_per_meal=float(request.budget * Decimal("0.02")),  # 2% of budget per meal
                cuisine_preferences=[pref.value for pref in request.preferences]
            )
            
            # Convert API results to RestaurantOption objects
            restaurants = []
            if restaurant_results.get("restaurants"):
                for restaurant_data in restaurant_results["restaurants"][:4]:  # Top 4 restaurants
                    restaurants.append(RestaurantOption(
                        id=restaurant_data.get("id", f"restaurant_{len(restaurants)+1}"),
                        name=restaurant_data.get("name", "Restaurant"),
                        rating=float(restaurant_data.get("rating", 4.0)),
                        price_level=int(restaurant_data.get("price_level", 2)),
                        address=restaurant_data.get("address", "City Center"),
                        cuisine_types=restaurant_data.get("cuisine_types", ["International"]),
                        estimated_cost=Decimal(str(restaurant_data.get("estimated_cost", 30))),
                        reviews_count=int(restaurant_data.get("reviews_count", 100)),
                        phone=restaurant_data.get("phone", ""),
                        website=restaurant_data.get("website", ""),
                        opening_hours=restaurant_data.get("opening_hours", []),
                        specialties=restaurant_data.get("specialties", [])
                    ))
        except Exception as e:
            print(f"❌ Error fetching restaurants: {e}")
            # Fallback to mock restaurant data
            restaurants = [
                RestaurantOption(
                    id="rest_001",
                    name="Local Cuisine Restaurant",
                    rating=4.5,
                    price_level=2,
                    address="Downtown Area",
                    cuisine_types=["Local", "Traditional"],
                    estimated_cost=Decimal("35"),
                    reviews_count=150,
                    phone="+1-555-0123",
                    website="",
                    opening_hours=["Mon-Sun: 11:00 AM - 10:00 PM"],
                    specialties=["Local specialties", "Fresh ingredients"]
                ),
                RestaurantOption(
                    id="rest_002", 
                    name="Fine Dining Experience",
                    rating=4.8,
                    price_level=3,
                    address="Arts District",
                    cuisine_types=["International", "Fine Dining"],
                    estimated_cost=Decimal("65"),
                    reviews_count=85,
                    phone="+1-555-0456",
                    website="",
                    opening_hours=["Tue-Sat: 6:00 PM - 11:00 PM"],
                    specialties=["Chef's special", "Wine pairing"]
                )
            ]

        # Calculate costs including restaurants
        flight_costs = sum(f.price for f in flights)
        hotel_costs = sum(h.total_price for h in hotels) 
        activity_costs = sum(a.price for a in activities)
        restaurant_costs = sum(r.estimated_cost for r in restaurants)
        
        total_cost = Decimal(str(flight_costs + hotel_costs + activity_costs + restaurant_costs))
        savings = request.budget - total_cost

        budget_breakdown = {
            "flights": flight_costs,
            "hotels": hotel_costs,
            "activities": activity_costs,
            "restaurants": restaurant_costs,
            "remaining": savings
        }

        # Generate detailed daily schedule showing all selected activities
        try:
            daily_schedule = self._generate_daily_schedule(request, activities)
        except Exception as e:
            print(f"❌ Error generating daily schedule: {e}")
            # Fallback to simple schedule
            duration_days = (request.end_date - request.start_date).days
            daily_schedule = [
                {
                    "date": (request.start_date + timedelta(days=day)).isoformat(),
                    "day_number": day + 1,
                    "activities": [],
                    "estimated_cost": 0
                }
                for day in range(duration_days)
            ]

        return TravelItinerary(
            request=request,
            flights=flights,
            hotels=hotels,
            activities=activities,
            restaurants=restaurants,
            total_cost=total_cost,
            savings=savings,
            daily_schedule=daily_schedule,
            budget_breakdown=budget_breakdown
        )
    
    def _generate_daily_schedule(self, request: TravelRequest, activities: List[ActivityOption]) -> List[Dict[str, Any]]:
        """Generate a day-by-day schedule with detailed activity information"""
        schedule = []
        
        # Calculate duration from dates
        duration_days = (request.end_date - request.start_date).days
        
        for day in range(duration_days):
            current_date = request.start_date + timedelta(days=day)
            # Distribute activities across days (1-2 activities per day)
            day_activities = activities[day:day+2] if activities and day < len(activities) else []
            
            # Create detailed activity info for this day
            day_activity_details = []
            day_cost = Decimal("0")
            
            for activity in day_activities:
                day_activity_details.append({
                    "name": activity.name,
                    "type": activity.type,
                    "description": activity.description,
                    "price": float(activity.price),
                    "duration": activity.duration,
                    "rating": activity.rating,
                    "location": activity.location
                })
                day_cost += activity.price
            
            schedule.append({
                "date": current_date.isoformat(),
                "day_number": day + 1,
                "activities": day_activity_details,
                "estimated_cost": float(day_cost)
            })
            
        return schedule
    
    async def _find_flights(self, request: TravelRequest, budget: Decimal) -> List[FlightOption]:
        """Find flight options using real Flight API"""
        try:
            from .travel_apis import FlightBookingAPI, FlightSearchParams
            
            flight_api = FlightBookingAPI()
            flight_params = FlightSearchParams(
                origin=request.departure_location,
                destination=request.destination,
                departure_date=request.start_date,
                return_date=request.end_date,
                passengers=request.travelers,
                max_price=budget * Decimal("0.6")  # 60% of budget for flights
            )
            
            flight_results = await flight_api.search_flights(flight_params)
            
            # Convert API results to FlightOption objects
            flights = []
            for flight_data in flight_results[:4]:  # Top 4 flights
                try:
                    # Parse departure time (handle various formats)
                    departure_str = flight_data.get("departure_time", "")
                    if departure_str:
                        # Try to parse ISO format or create mock time
                        try:
                            departure_time = datetime.fromisoformat(departure_str.replace('Z', '+00:00'))
                        except:
                            departure_time = datetime.combine(request.start_date, datetime.min.time().replace(hour=8))
                    else:
                        departure_time = datetime.combine(request.start_date, datetime.min.time().replace(hour=8))
                    
                    # Parse arrival time
                    arrival_str = flight_data.get("arrival_time", "")
                    if arrival_str:
                        try:
                            arrival_time = datetime.fromisoformat(arrival_str.replace('Z', '+00:00'))
                        except:
                            arrival_time = datetime.combine(request.start_date, datetime.min.time().replace(hour=14))
                    else:
                        arrival_time = datetime.combine(request.start_date, datetime.min.time().replace(hour=14))
                    
                    flight = FlightOption(
                        flight_id=flight_data.get("id", f"flight_{len(flights)+1}"),
                        airline=flight_data.get("airline", "Unknown Airline"),
                        aircraft=flight_data.get("aircraft"),
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        departure_airport=flight_data.get("departure_airport", ""),
                        arrival_airport=flight_data.get("arrival_airport", ""),
                        price=Decimal(str(flight_data.get("price", 450))),
                        stops=flight_data.get("stops", 0),
                        duration=flight_data.get("duration", "6h 30m"),
                        travel_class=flight_data.get("class", "Economy"),
                        available_seats=f"{flight_data.get('available_seats', 0)} seats available",
                        instant_confirmation=bool(flight_data.get("instant_confirmation", True))
                    )
                    flights.append(flight)
                except Exception as parse_error:
                    print(f"⚠️  Error parsing flight data: {parse_error}")
                    continue
            
            if flights:
                return flights
            else:
                # Fallback to mock data if no flights found
                return self._mock_flights(request, budget)
                
        except Exception as e:
            print(f"❌ Flight API error in travel agent: {e}")
            return self._mock_flights(request, budget)
    
    def _mock_flights(self, request: TravelRequest, budget: Decimal) -> List[FlightOption]:
        """Fallback mock flight data"""
        return [
            FlightOption(
                flight_id="flight_001",
                airline="American Airlines",
                aircraft="Boeing 737-800",
                departure_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=8)),
                arrival_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=14, minute=30)),
                departure_airport="JFK",
                arrival_airport="CDG",
                price=min(budget * Decimal("0.4"), Decimal("540")),
                stops=0,
                duration="6h 30m",
                travel_class="Economy",
                available_seats="15 seats available",
                instant_confirmation=True
            ),
            FlightOption(
                flight_id="flight_002",
                airline="Delta Air Lines",
                aircraft="Airbus A320",
                departure_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=12)),
                arrival_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=20, minute=45)),
                departure_airport="JFK",
                arrival_airport="CDG",
                price=min(budget * Decimal("0.3"), Decimal("450")),
                stops=1,
                duration="8h 45m",
                travel_class="Economy",
                available_seats="8 seats available",
                instant_confirmation=True
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
import os

# Create frontend directory path
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
        import traceback
        print(f"❌ ERROR in plan_trip: {type(e).__name__}: {str(e)}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to plan trip: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TravelMaster AI Agent"}


@app.get("/api/restaurants/{destination}")
async def get_restaurants(destination: str, budget_per_meal: float = 50.0, cuisine: Optional[str] = None):
    """Search for restaurants in a specific destination"""
    try:
        cuisine_preferences = [cuisine] if cuisine else []
        restaurant_results = await travel_service.travel_apis.search_restaurants(
            destination=destination,
            max_budget_per_meal=budget_per_meal,
            cuisine_preferences=cuisine_preferences
        )
        
        return {
            "destination": destination,
            "budget_per_meal": budget_per_meal,
            "restaurants": restaurant_results.get("restaurants", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search restaurants: {str(e)}")


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
    print("🌐 Web Interface: http://localhost:8000")
    print("🎤 Voice interaction available in browser!")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("")
    print("Try saying: 'I want to go to Paris with a budget of 3000 dollars for a luxury trip'")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
