#!/usr/bin/env python3
"""
Quick Demo Setup - Fast Loading Travel Agents for Shell Hacks Demo
Creates working agents that return realistic-looking data instantly.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Quick data models
class FlightSearch(BaseModel):
    origin: str
    destination: str  
    departure_date: str
    passengers: int = 2
    budget: float = 1000

class HotelSearch(BaseModel):
    destination: str
    check_in: str
    check_out: str
    guests: int = 2
    budget: float = 500

class ActivitySearch(BaseModel):
    destination: str
    budget_per_person: float = 100
    group_size: int = 2

# Quick Flight Agent
def create_flight_agent():
    app = FastAPI(title="Quick Flight Agent")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    
    @app.get("/")
    async def info():
        return {
            "agent": "FlightBookingAgent",
            "status": "active",
            "capabilities": ["flight_search", "flight_booking"]
        }
    
    @app.post("/api/search-flights")
    async def search_flights(request: FlightSearch):
        # Fast realistic flight data
        return {
            "success": True,
            "flights": [
                {
                    "flight_id": "AF123",
                    "airline": "Air France",
                    "departure_airport": request.origin,
                    "arrival_airport": request.destination,
                    "departure_time": "08:30",
                    "arrival_time": "14:45",
                    "price": 450.00,
                    "duration": "8h 15m",
                    "stops": 0,
                    "status": "Available"
                },
                {
                    "flight_id": "BA456", 
                    "airline": "British Airways",
                    "departure_airport": request.origin,
                    "arrival_airport": request.destination,
                    "departure_time": "12:15",
                    "arrival_time": "18:30",
                    "price": 520.00,
                    "duration": "8h 15m", 
                    "stops": 0,
                    "status": "Available"
                }
            ],
            "agent_id": "flight-booking-agent"
        }
    
    return app

# Quick Hotel Agent  
def create_hotel_agent():
    app = FastAPI(title="Quick Hotel Agent")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    
    @app.get("/")
    async def info():
        return {
            "agent": "HotelBookingAgent",
            "status": "active", 
            "capabilities": ["hotel_search", "hotel_booking"]
        }
    
    @app.post("/api/search-hotels")
    async def search_hotels(request: HotelSearch):
        return {
            "success": True,
            "hotels": [
                {
                    "hotel_id": "HTL001",
                    "name": "Grand Hotel Paris",
                    "location": f"{request.destination} City Center",
                    "rating": 4.5,
                    "price_per_night": 180.00,
                    "total_cost": 540.00,
                    "amenities": ["WiFi", "Spa", "Restaurant"],
                    "status": "Available"
                },
                {
                    "hotel_id": "HTL002",
                    "name": "Boutique Hotel Elite",
                    "location": f"{request.destination} Downtown", 
                    "rating": 4.3,
                    "price_per_night": 220.00,
                    "total_cost": 660.00,
                    "amenities": ["WiFi", "Gym", "Breakfast"],
                    "status": "Available"
                }
            ],
            "agent_id": "hotel-booking-agent"
        }
    
    return app

# Quick Activity Agent
def create_activity_agent():
    app = FastAPI(title="Quick Activity Agent") 
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    
    @app.get("/")
    async def info():
        return {
            "agent": "ActivityPlanningAgent",
            "status": "active",
            "capabilities": ["activity_search", "restaurant_recommendations"]
        }
    
    @app.post("/api/search-restaurants")
    async def search_restaurants(request: ActivitySearch):
        return {
            "success": True,
            "restaurants": [
                {
                    "restaurant_id": "REST001",
                    "name": "Le Gourmet Bistro",
                    "cuisine": "French",
                    "rating": 4.6,
                    "avg_price_per_person": 65.00,
                    "address": f"{request.destination} - Fine Dining District",
                    "total_cost": request.budget_per_person * request.group_size
                },
                {
                    "restaurant_id": "REST002", 
                    "name": "Casual Corner Cafe",
                    "cuisine": "International",
                    "rating": 4.2,
                    "avg_price_per_person": 35.00,
                    "address": f"{request.destination} - Local Area", 
                    "total_cost": 70.00
                }
            ],
            "agent_id": "activity-planning-agent"
        }
    
    @app.post("/api/search-activities")
    async def search_activities(request: ActivitySearch):
        return {
            "success": True,
            "activities": [
                {
                    "activity_id": "ACT001",
                    "name": "City Walking Tour",
                    "category": "sightseeing",
                    "price": 25.00,
                    "duration": "3 hours",
                    "rating": 4.4,
                    "location": f"{request.destination} Historic District"
                },
                {
                    "activity_id": "ACT002",
                    "name": "Museum Visit", 
                    "category": "cultural",
                    "price": 18.00,
                    "duration": "2 hours",
                    "rating": 4.7,
                    "location": f"{request.destination} Arts Quarter"
                }
            ],
            "agent_id": "activity-planning-agent"
        }
    
    return app

# Start all agents
async def start_agents():
    print("🚀 Starting Quick Demo Agents...")
    
    # Start Flight Agent on 8001
    flight_app = create_flight_agent()
    print("✈️ Flight Agent starting on port 8001...")
    
    # Start Hotel Agent on 8002  
    hotel_app = create_hotel_agent()
    print("🏨 Hotel Agent starting on port 8002...")
    
    # Start Activity Agent on 8003
    activity_app = create_activity_agent()
    print("🎯 Activity Agent starting on port 8003...")
    
    # Run agents concurrently
    await asyncio.gather(
        uvicorn.run(flight_app, host="0.0.0.0", port=8001, log_level="warning"),
        uvicorn.run(hotel_app, host="0.0.0.0", port=8002, log_level="warning"), 
        uvicorn.run(activity_app, host="0.0.0.0", port=8003, log_level="warning")
    )

if __name__ == "__main__":
    print("🎭 Shell Hacks Quick Demo - Fast Loading Agents")
    print("⚡ These agents return realistic data instantly for demo purposes")
    asyncio.run(start_agents())