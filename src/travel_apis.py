"""
External API Integration Services for TravelMaster

This module provides integration with real travel booking APIs
including flights, hotels, and activities.
"""

import asyncio
import httpx
from typing import List, Dict, Any, Optional, cast
from datetime import datetime, date
from decimal import Decimal
import os
from dataclasses import dataclass


@dataclass
class FlightSearchParams:
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    passengers: int = 1
    max_price: Optional[Decimal] = None


@dataclass
class HotelSearchParams:
    destination: str
    check_in: date
    check_out: date
    guests: int = 1
    max_price_per_night: Optional[Decimal] = None


class FlightBookingAPI:
    """Integration with flight booking APIs (Amadeus, Skyscanner, etc.)"""
    
    def __init__(self):
        self.api_key = "CHxXACuhjtuRfXFr8GwAnSZ0Nz53w8SY"
        self.api_secret = "sAmlzGXP4eMlhJ1Y"
        self.base_url = "https://test.api.amadeus.com"
        self.access_token = None
        
        # Airport mapping for common destinations
        self.airport_codes = {
            "paris": "CDG", "london": "LHR", "tokyo": "NRT",
            "new york": "JFK", "los angeles": "LAX", "miami": "MIA",
            "barcelona": "BCN", "rome": "FCO", "amsterdam": "AMS",
            "berlin": "BER", "madrid": "MAD"
        }
        
        self.airport_names = {
            "CDG": "Charles de Gaulle Airport",
            "LHR": "Heathrow Airport",
            "NRT": "Narita International Airport", 
            "JFK": "John F. Kennedy International Airport",
            "LAX": "Los Angeles International Airport",
            "BCN": "Barcelona-El Prat Airport",
            "FCO": "Leonardo da Vinci-Fiumicino Airport",
            "AMS": "Amsterdam Airport Schiphol",
            "BER": "Berlin Brandenburg Airport",
            "MAD": "Madrid-Barajas Airport"
        }
    
    def _get_airport_code(self, location: str) -> str:
        """Get airport code for a location"""
        location_lower = location.lower()
        for city, code in self.airport_codes.items():
            if city in location_lower:
                return code
        return location[:3].upper()  # Fallback to first 3 letters
    
    def _get_airport_name(self, location: str) -> str:
        """Get airport name for a location"""
        code = self._get_airport_code(location)
        return self.airport_names.get(code, f"{location} Airport")
    
    async def get_access_token(self) -> str:
        """Get OAuth access token for Amadeus API"""
        if self.access_token:
            return self.access_token
            
        # Mock token for development - replace with real OAuth flow
        self.access_token = "mock_access_token"
        return self.access_token
    
    async def search_flights(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """Search for flights using Amadeus API"""
        try:
            token = await self.get_access_token()
            
            # For development, return mock data
            # In production, make actual API calls to Amadeus
            return await self._mock_flight_search(params)
            
        except Exception as e:
            print(f"Flight search error: {e}")
            return await self._mock_flight_search(params)
    
    async def _mock_flight_search(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """Mock flight search results for development"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        base_price = min(params.max_price or Decimal("800"), Decimal("600"))
        
        return [
            {
                "id": "flight_001",
                "airline": "American Airlines",
                "flight_number": "AA1234",
                "departure_airport": self._get_airport_code(params.origin),
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": self._get_airport_code(params.destination),
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=8)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=14, minute=30)),
                "duration": "6h 30m",
                "stops": 0,
                "price": base_price * Decimal("0.9"),
                "currency": "USD",
                "booking_class": "Economy",
                "available_seats": 15,
                "aircraft": "Boeing 737-800"
            },
            {
                "id": "flight_002", 
                "airline": "Delta Air Lines",
                "flight_number": "DL5678",
                "departure_airport": self._get_airport_code(params.origin),
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": self._get_airport_code(params.destination),
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=12)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=20, minute=45)),
                "duration": "8h 45m",
                "stops": 1,
                "price": base_price * Decimal("0.75"),
                "currency": "USD",
                "booking_class": "Economy",
                "available_seats": 8,
                "aircraft": "Airbus A320"
            },
            {
                "id": "flight_003",
                "airline": "United Airlines", 
                "flight_number": "UA9012",
                "departure_airport": self._get_airport_code(params.origin),
                "departure_airport_name": self._get_airport_name(params.origin),
                "arrival_airport": self._get_airport_code(params.destination),
                "arrival_airport_name": self._get_airport_name(params.destination),
                "departure_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=15)),
                "arrival_time": datetime.combine(params.departure_date, datetime.min.time().replace(hour=21, minute=15)),
                "duration": "6h 15m",
                "stops": 0,
                "price": base_price * Decimal("1.1"),
                "currency": "USD", 
                "booking_class": "Economy Plus",
                "available_seats": 22,
                "aircraft": "Boeing 777-300ER"
            }
        ]


class HotelBookingAPI:
    """Integration with hotel booking APIs (Booking.com, Hotels.com, etc.)"""
    
    def __init__(self):
        self.booking_com_key = os.getenv("BOOKING_COM_API_KEY", "test_key")
        self.base_url = "https://distribution-xml.booking.com"
    
    async def search_hotels(self, params: HotelSearchParams) -> List[Dict[str, Any]]:
        """Search for hotels using Booking.com API"""
        try:
            # For development, return mock data
            # In production, integrate with real Booking.com API
            return await self._mock_hotel_search(params)
            
        except Exception as e:
            print(f"Hotel search error: {e}")
            return await self._mock_hotel_search(params)
    
    async def _mock_hotel_search(self, params: HotelSearchParams) -> List[Dict[str, Any]]:
        """Mock hotel search results for development"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        nights = (params.check_out - params.check_in).days
        max_price = params.max_price_per_night or Decimal("200")
        
        return [
            {
                "id": "hotel_001",
                "name": "Grand City Hotel",
                "rating": 4.5,
                "review_score": 8.7,
                "total_reviews": 2847,
                "location": "City Center",
                "address": f"123 Main St, {params.destination}",
                "price_per_night": max_price * Decimal("0.8"),
                "total_price": max_price * Decimal("0.8") * nights,
                "currency": "USD",
                "amenities": ["Free WiFi", "Pool", "Fitness Center", "Restaurant", "Room Service"],
                "room_type": "Deluxe Double Room",
                "breakfast_included": True,
                "cancellation_policy": "Free cancellation until 24 hours before check-in",
                "distance_to_center": "0.2 km"
            },
            {
                "id": "hotel_002",
                "name": "Budget Inn Express",
                "rating": 3.8,
                "review_score": 7.9,
                "total_reviews": 1523,
                "location": "Near Airport",
                "address": f"456 Airport Rd, {params.destination}",
                "price_per_night": max_price * Decimal("0.5"),
                "total_price": max_price * Decimal("0.5") * nights,
                "currency": "USD",
                "amenities": ["Free WiFi", "Parking", "24h Reception"],
                "room_type": "Standard Double Room",
                "breakfast_included": False,
                "cancellation_policy": "Free cancellation until 48 hours before check-in",
                "distance_to_center": "8.5 km"
            },
            {
                "id": "hotel_003",
                "name": "Luxury Resort & Spa",
                "rating": 5.0,
                "review_score": 9.2,
                "total_reviews": 892,
                "location": "Beachfront",
                "address": f"789 Ocean View Ave, {params.destination}",
                "price_per_night": max_price * Decimal("1.5"),
                "total_price": max_price * Decimal("1.5") * nights,
                "currency": "USD", 
                "amenities": ["Private Beach", "Spa", "Multiple Restaurants", "Pool", "Concierge", "Room Service"],
                "room_type": "Ocean View Suite",
                "breakfast_included": True,
                "cancellation_policy": "Free cancellation until 7 days before check-in",
                "distance_to_center": "12.3 km"
            }
        ]


class ActivityBookingAPI:
    """Integration with activity booking APIs (GetYourGuide, Viator, etc.)"""
    
    def __init__(self):
        self.getyourguide_key = os.getenv("GETYOURGUIDE_API_KEY", "test_key")
        self.viator_key = os.getenv("VIATOR_API_KEY", "test_key")
    
    async def search_activities(self, destination: str, max_budget: Decimal, preferences: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for activities and tours"""
        try:
            # For development, return mock data
            # In production, integrate with GetYourGuide/Viator APIs
            return await self._mock_activity_search(destination, max_budget, preferences or [])
            
        except Exception as e:
            print(f"Activity search error: {e}")
            return await self._mock_activity_search(destination, max_budget, preferences or [])
    
    async def _mock_activity_search(self, destination: str, max_budget: Decimal, preferences: List[str]) -> List[Dict[str, Any]]:
        """Mock activity search results for development"""
        await asyncio.sleep(0.4)  # Simulate API delay
        
        base_activities = [
            {
                "id": "activity_001",
                "name": f"Historic {destination} Walking Tour",
                "category": "sightseeing",
                "description": f"Explore the historic landmarks and hidden gems of {destination} with a knowledgeable local guide.",
                "duration": "3 hours",
                "price": min(max_budget * Decimal("0.2"), Decimal("45")),
                "currency": "USD",
                "rating": 4.6,
                "total_reviews": 1247,
                "highlights": ["Historic landmarks", "Local stories", "Photo opportunities"],
                "includes": ["Professional guide", "Walking tour", "Historical insights"],
                "meeting_point": f"Central Square, {destination}",
                "languages": ["English", "Spanish"],
                "group_size": "Max 15 people"
            },
            {
                "id": "activity_002", 
                "name": f"Culinary Food Tour in {destination}",
                "category": "food_and_drink",
                "description": f"Taste authentic local cuisine and learn about {destination}'s food culture from expert guides.",
                "duration": "2.5 hours",
                "price": min(max_budget * Decimal("0.35"), Decimal("75")),
                "currency": "USD",
                "rating": 4.8,
                "total_reviews": 892,
                "highlights": ["Local food tasting", "Cultural insights", "Hidden food spots"],
                "includes": ["Food samples", "Expert guide", "Cultural stories"],
                "meeting_point": f"Food Market, {destination}",
                "languages": ["English"],
                "group_size": "Max 12 people"
            },
            {
                "id": "activity_003",
                "name": f"{destination} Museum and Art Gallery Pass",
                "category": "cultural",
                "description": f"Skip-the-line access to {destination}'s top museums and art galleries.",
                "duration": "Full day",
                "price": min(max_budget * Decimal("0.25"), Decimal("60")),
                "currency": "USD", 
                "rating": 4.4,
                "total_reviews": 634,
                "highlights": ["Skip-the-line access", "Multiple venues", "Audio guides"],
                "includes": ["Museum entries", "Audio guide", "Map"],
                "meeting_point": "Self-guided",
                "languages": ["English", "Spanish", "French"],
                "group_size": "Individual"
            },
            {
                "id": "activity_004",
                "name": f"Adventure {destination} Bike Tour", 
                "category": "adventure",
                "description": f"Explore {destination}'s scenic routes and hidden paths on a guided bike tour.",
                "duration": "4 hours",
                "price": min(max_budget * Decimal("0.4"), Decimal("85")),
                "currency": "USD",
                "rating": 4.7,
                "total_reviews": 456,
                "highlights": ["Scenic routes", "Adventure cycling", "Local insights"],
                "includes": ["Bike rental", "Helmet", "Guide", "Water"],
                "meeting_point": f"Bike Shop, {destination}",
                "languages": ["English"],
                "group_size": "Max 8 people"
            }
        ]
        
        # Filter activities based on preferences
        if preferences:
            filtered_activities = []
            for activity in base_activities:
                if any(pref.lower() in activity["category"].lower() or 
                      pref.lower() in activity["name"].lower() or
                      pref.lower() in activity["description"].lower() 
                      for pref in preferences):
                    filtered_activities.append(activity)
            return filtered_activities or base_activities[:2]  # Return at least 2 activities
        
        return base_activities


class TravelAPIManager:
    """Main manager for all travel API integrations"""
    
    def __init__(self):
        self.flight_api = FlightBookingAPI()
        self.hotel_api = HotelBookingAPI()
        self.activity_api = ActivityBookingAPI()
    
    async def search_all(self, destination: str, departure_location: str, 
                        start_date: date, end_date: date, 
                        travelers: int, budget: Decimal,
                        preferences: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search flights, hotels, and activities simultaneously"""
        
        # Calculate budget allocation
        flight_budget = budget * Decimal("0.4")  # 40% for flights
        hotel_budget = budget * Decimal("0.35")   # 35% for hotels  
        activity_budget = budget * Decimal("0.2") # 20% for activities (5% buffer)
        
        # Create search parameters
        flight_params = FlightSearchParams(
            origin=departure_location,
            destination=destination,
            departure_date=start_date,
            return_date=end_date,
            passengers=travelers,
            max_price=flight_budget
        )
        
        nights = (end_date - start_date).days
        hotel_params = HotelSearchParams(
            destination=destination,
            check_in=start_date,
            check_out=end_date,
            guests=travelers,
            max_price_per_night=hotel_budget / nights if nights > 0 else hotel_budget
        )
        
        # Execute searches concurrently
        results = await asyncio.gather(
            self.flight_api.search_flights(flight_params),
            self.hotel_api.search_hotels(hotel_params),
            self.activity_api.search_activities(destination, activity_budget, preferences),
            return_exceptions=True
        )
        
        # Handle results with proper typing
        flights = cast(List[Dict[str, Any]], results[0] if not isinstance(results[0], Exception) else [])
        hotels = cast(List[Dict[str, Any]], results[1] if not isinstance(results[1], Exception) else [])
        activities = cast(List[Dict[str, Any]], results[2] if not isinstance(results[2], Exception) else [])
        
        return {
            "flights": flights,
            "hotels": hotels, 
            "activities": activities
        }


# Export the main API manager
travel_apis = TravelAPIManager()