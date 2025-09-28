"""
Gemini AI Agent for Trip Planning and Management

This module provides AI-powered trip summarization, itinerary generation,
and disruption handling using Google's Gemini API.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import os
import httpx
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TripEvent:
    """Represents a single event in the trip itinerary"""
    date: str
    start_time: str
    end_time: str
    title: str
    type: str  # flight, hotel, restaurant, activity, sightseeing
    location: str
    description: str
    cost: float
    confirmation_number: Optional[str] = None
    contact_info: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class DailyItinerary:
    """Represents a full day's schedule"""
    date: str
    day_of_week: str
    location: str
    events: List[TripEvent]
    daily_budget: float
    weather_note: Optional[str] = None


class GeminiTripAgent:
    """AI agent for comprehensive trip planning and management"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        if not self.api_key:
            print("⚠️  Google Gemini API key not found. Set GEMINI_API_KEY in .env file")
            print("   Get your key at: https://makersuite.google.com/app/apikey")
        else:
            print("✅ Gemini AI agent initialized successfully")
    
    async def generate_comprehensive_itinerary(self, trip_data: Dict[str, Any], 
                                             special_instructions: Optional[str] = None) -> List[DailyItinerary]:
        """
        Generate a comprehensive daily itinerary using Gemini AI
        
        Args:
            trip_data: Complete trip data including flights, hotels, restaurants, activities
            special_instructions: User's special preferences or requirements
        
        Returns:
            List of daily itineraries with scheduled events
        """
        if not self.api_key:
            return await self._generate_fallback_itinerary(trip_data)
        
        try:
            # Prepare the prompt for Gemini
            prompt = self._create_itinerary_prompt(trip_data, special_instructions)
            
            # Call Gemini API
            response = await self._call_gemini_api(prompt, "generate-itinerary")
            
            # Parse the response into structured itinerary
            itinerary = await self._parse_itinerary_response(response, trip_data)
            
            print(f"✅ Generated comprehensive {len(itinerary)}-day itinerary via Gemini AI")
            return itinerary
            
        except Exception as e:
            print(f"❌ Gemini itinerary generation failed: {e}")
            return await self._generate_fallback_itinerary(trip_data)
    
    def _create_itinerary_prompt(self, trip_data: Dict[str, Any], special_instructions: Optional[str]) -> str:
        """Create a comprehensive prompt for Gemini to generate the itinerary"""
        
        # Extract key information
        request = trip_data.get("request", {})
        flights = trip_data.get("flights", [])
        hotels = trip_data.get("hotels", [])
        restaurants = trip_data.get("restaurants", [])
        activities = trip_data.get("activities", [])
        budget_breakdown = trip_data.get("budget_breakdown", {})
        
        prompt = f"""You are an expert travel planner. Create a detailed day-by-day itinerary for this trip:

TRIP DETAILS:
- Destination: {request.get('destination', 'Unknown')}
- Departure: {request.get('departure_location', 'Unknown')}
- Dates: {request.get('start_date', 'Unknown')} to {request.get('end_date', 'Unknown')}
- Travelers: {request.get('travelers', 1)}
- Budget: ${request.get('budget', 0)}
- Preferences: {', '.join(request.get('preferences', []))}

BOOKED COMPONENTS:

FLIGHTS:
"""
        
        for i, flight in enumerate(flights[:4], 1):
            trip_type = flight.get('trip_type', 'unknown')
            prompt += f"  {i}. {flight.get('airline', 'Unknown')} {flight.get('flight_number', '')} ({trip_type.title()})\n"
            prompt += f"     {flight.get('departure_airport', '')} → {flight.get('arrival_airport', '')} on {flight.get('departure_time', '')[:10]}\n"
            prompt += f"     Departure: {flight.get('departure_time', '')[-8:] if flight.get('departure_time', '') else 'TBD'}\n\n"
        
        prompt += "\nHOTELS:\n"
        for i, hotel in enumerate(hotels[:2], 1):
            prompt += f"  {i}. {hotel.get('name', 'Hotel')} - ${hotel.get('price_per_night', 0)}/night\n"
            prompt += f"     {hotel.get('location', 'City Center')}\n"
            prompt += f"     Check-in: {hotel.get('check_in', '')}, Check-out: {hotel.get('check_out', '')}\n\n"
        
        prompt += "\nRESTAURANTS:\n"
        for i, restaurant in enumerate(restaurants[:4], 1):
            prompt += f"  {i}. {restaurant.get('name', 'Restaurant')} - {restaurant.get('rating', 'N/A')}★\n"
            prompt += f"     Cuisine: {', '.join(restaurant.get('cuisine_types', ['International']))}\n"
            prompt += f"     Cost: ~${restaurant.get('estimated_cost', 0)}\n\n"
        
        prompt += "\nACTIVITIES:\n"
        for i, activity in enumerate(activities[:6], 1):
            prompt += f"  {i}. {activity.get('name', 'Activity')} - {activity.get('rating', 'N/A')}★\n"
            prompt += f"     Type: {activity.get('type', 'Sightseeing')}, Duration: {activity.get('duration', 'Unknown')}\n"
            prompt += f"     Cost: ${activity.get('price', 0)}\n\n"
        
        if special_instructions:
            prompt += f"\nSPECIAL INSTRUCTIONS:\n{special_instructions}\n\n"
        
        prompt += """
REQUIREMENTS:
1. Create a realistic day-by-day schedule with specific times
2. Balance activities with rest periods
3. Consider travel time between locations
4. Include meals at recommended restaurants
5. Distribute activities logically across days
6. Provide backup indoor options for each day
7. Include estimated costs for each day
8. Add helpful travel tips and local insights

RESPONSE FORMAT (JSON):
{
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_of_week": "Monday",
      "location": "City, Country",
      "events": [
        {
          "start_time": "09:00",
          "end_time": "10:30",
          "title": "Event Title",
          "type": "activity|restaurant|sightseeing|travel",
          "location": "Specific Location",
          "description": "Detailed description",
          "cost": 25.0,
          "notes": "Helpful tips"
        }
      ],
      "daily_budget": 150.0,
      "weather_note": "Pack umbrella if rainy season"
    }
  ],
  "total_planned_cost": 800.0,
  "trip_highlights": ["Top 3 must-do activities"],
  "local_tips": ["Important local customs", "Best times to visit attractions"],
  "emergency_contacts": {
    "hotel": "+1-555-0123",
    "local_emergency": "911",
    "embassy": "+1-555-0456"
  }
}

Generate a comprehensive, realistic itinerary:"""
        
        return prompt
    
    async def _call_gemini_api(self, prompt: str, task_type: str) -> str:
        """Make API call to Gemini"""
        
        url = f"{self.base_url}/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if "candidates" in data and data["candidates"]:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return content
            else:
                raise Exception("No content generated by Gemini")
    
    async def _parse_itinerary_response(self, response: str, trip_data: Dict[str, Any]) -> List[DailyItinerary]:
        """Parse Gemini's response into structured itinerary"""
        
        try:
            # Try to extract JSON from the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                itineraries = []
                
                for day_data in data.get("days", []):
                    events = []
                    
                    for event_data in day_data.get("events", []):
                        event = TripEvent(
                            date=day_data["date"],
                            start_time=event_data.get("start_time", "09:00"),
                            end_time=event_data.get("end_time", "10:00"),
                            title=event_data.get("title", "Activity"),
                            type=event_data.get("type", "activity"),
                            location=event_data.get("location", "City Center"),
                            description=event_data.get("description", ""),
                            cost=float(event_data.get("cost", 0)),
                            notes=event_data.get("notes")
                        )
                        events.append(event)
                    
                    daily_itinerary = DailyItinerary(
                        date=day_data["date"],
                        day_of_week=day_data.get("day_of_week", ""),
                        location=day_data.get("location", ""),
                        events=events,
                        daily_budget=float(day_data.get("daily_budget", 0)),
                        weather_note=day_data.get("weather_note")
                    )
                    itineraries.append(daily_itinerary)
                
                return itineraries
            
        except Exception as e:
            print(f"❌ Failed to parse Gemini response: {e}")
        
        # Fallback if parsing fails
        return await self._generate_fallback_itinerary(trip_data)
    
    async def _generate_fallback_itinerary(self, trip_data: Dict[str, Any]) -> List[DailyItinerary]:
        """Generate a basic itinerary if Gemini fails"""
        
        request = trip_data.get("request", {})
        activities = trip_data.get("activities", [])
        restaurants = trip_data.get("restaurants", [])
        
        try:
            start_date = datetime.fromisoformat(request.get("start_date", "2025-01-01"))
            end_date = datetime.fromisoformat(request.get("end_date", "2025-01-03"))
        except:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=2)
        
        itineraries = []
        current_date = start_date
        
        while current_date < end_date:
            events = []
            
            # Morning activity
            if activities:
                activity = activities[len(itineraries) % len(activities)]
                events.append(TripEvent(
                    date=current_date.isoformat()[:10],
                    start_time="09:00",
                    end_time="11:30",
                    title=activity.get("name", "Morning Activity"),
                    type="activity",
                    location=activity.get("location", "City Center"),
                    description=activity.get("description", "Explore local attractions"),
                    cost=float(activity.get("price", 25))
                ))
            
            # Lunch
            if restaurants:
                restaurant = restaurants[len(itineraries) % len(restaurants)]
                events.append(TripEvent(
                    date=current_date.isoformat()[:10],
                    start_time="12:30",
                    end_time="14:00",
                    title=f"Lunch at {restaurant.get('name', 'Local Restaurant')}",
                    type="restaurant",
                    location=restaurant.get("address", "City Center"),
                    description=f"Enjoy {', '.join(restaurant.get('cuisine_types', ['local cuisine']))}",
                    cost=float(restaurant.get("estimated_cost", 30))
                ))
            
            # Afternoon sightseeing
            events.append(TripEvent(
                date=current_date.isoformat()[:10],
                start_time="15:00",
                end_time="17:00",
                title=f"Explore {request.get('destination', 'City')} Landmarks",
                type="sightseeing",
                location=request.get('destination', 'City Center'),
                description="Visit iconic landmarks and take photos",
                cost=15.0
            ))
            
            daily_itinerary = DailyItinerary(
                date=current_date.isoformat()[:10],
                day_of_week=current_date.strftime("%A"),
                location=request.get('destination', 'Destination'),
                events=events,
                daily_budget=sum(event.cost for event in events)
            )
            
            itineraries.append(daily_itinerary)
            current_date += timedelta(days=1)
        
        print(f"✅ Generated {len(itineraries)}-day fallback itinerary")
        return itineraries
    
    async def handle_trip_disruption(self, disruption: Dict[str, Any], 
                                   current_itinerary: List[DailyItinerary]) -> Dict[str, Any]:
        """
        Handle trip disruptions like flight delays, weather, etc.
        
        Args:
            disruption: Details about the disruption (type, severity, affected_dates)
            current_itinerary: Current planned itinerary
        
        Returns:
            Updated plans and alternative suggestions
        """
        if not self.api_key:
            return await self._handle_disruption_fallback(disruption, current_itinerary)
        
        try:
            prompt = self._create_disruption_prompt(disruption, current_itinerary)
            response = await self._call_gemini_api(prompt, "handle-disruption")
            
            return await self._parse_disruption_response(response)
            
        except Exception as e:
            print(f"❌ Disruption handling failed: {e}")
            return await self._handle_disruption_fallback(disruption, current_itinerary)
    
    def _create_disruption_prompt(self, disruption: Dict[str, Any], 
                                itinerary: List[DailyItinerary]) -> str:
        """Create prompt for handling disruptions"""
        
        prompt = f"""You are a travel crisis manager. Help handle this trip disruption:

DISRUPTION DETAILS:
- Type: {disruption.get('type', 'Unknown')}
- Severity: {disruption.get('severity', 'Medium')}
- Affected Dates: {disruption.get('affected_dates', [])}
- Description: {disruption.get('description', 'Unexpected issue occurred')}

CURRENT ITINERARY:
"""
        
        for day in itinerary:
            prompt += f"\n{day.date} ({day.day_of_week}) - {day.location}:\n"
            for event in day.events:
                prompt += f"  {event.start_time}-{event.end_time}: {event.title} (${event.cost})\n"
        
        prompt += """

REQUIREMENTS:
1. Provide immediate alternative options
2. Suggest rebooking strategies if needed
3. Identify backup activities for affected days
4. Calculate additional costs or savings
5. Provide clear action steps for the traveler
6. Include emergency contact information if needed

RESPONSE FORMAT (JSON):
{
  "urgency_level": "low|medium|high",
  "immediate_actions": ["Action 1", "Action 2"],
  "alternative_options": [
    {
      "type": "flight|hotel|activity",
      "original": "Original plan",
      "alternative": "New suggestion",
      "cost_difference": 50.0,
      "booking_info": "How to book"
    }
  ],
  "updated_schedule": [
    {
      "date": "YYYY-MM-DD",
      "changes": ["List of changes for this day"]
    }
  ],
  "total_cost_impact": 150.0,
  "traveler_notes": ["Important information for traveler"],
  "emergency_contacts": ["Relevant contact numbers"]
}

Provide comprehensive disruption management:"""
        
        return prompt
    
    async def _parse_disruption_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini's disruption response"""
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
                
        except Exception as e:
            print(f"❌ Failed to parse disruption response: {e}")
        
        return await self._handle_disruption_fallback({}, [])
    
    async def _handle_disruption_fallback(self, disruption: Dict[str, Any], 
                                        itinerary: List[DailyItinerary]) -> Dict[str, Any]:
        """Fallback disruption handling"""
        
        return {
            "urgency_level": "medium",
            "immediate_actions": [
                "Contact airline/hotel customer service",
                "Check for alternative options",
                "Review travel insurance coverage"
            ],
            "alternative_options": [
                {
                    "type": "general",
                    "original": "Current booking",
                    "alternative": "Contact service providers for alternatives",
                    "cost_difference": 0.0,
                    "booking_info": "Call customer service numbers"
                }
            ],
            "total_cost_impact": 0.0,
            "traveler_notes": [
                "Stay calm and contact service providers",
                "Document all changes for insurance claims",
                "Keep all receipts for additional expenses"
            ],
            "emergency_contacts": ["911", "Travel insurance hotline"]
        }


# Export the agent
gemini_agent = GeminiTripAgent()
