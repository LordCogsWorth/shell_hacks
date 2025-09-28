#!/usr/bin/env python3
"""
EMERGENCY FAST DEMO SYSTEM - Shell Hacks
No dependencies, pure FastAPI, instant responses
"""
import os
import json
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

class TripRequest(BaseModel):
    destination: str = "Paris"
    budget: float = 2000
    travelers: int = 2
    start_date: str = "2025-10-15"
    end_date: str = "2025-10-18"

app = FastAPI(title="TravelMaster Emergency Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "TravelMaster Demo Ready", "status": "active", "frontend": "/frontend/"}

@app.post("/api/plan-trip")
async def plan_trip_instant(request: TripRequest):
    """INSTANT trip planning - no API delays"""
    
    print(f"🚀 INSTANT Planning: {request.destination} for {request.travelers} people")
    
    # INSTANT realistic data
    flights = [
        {
            "flight_id": "AF123",
            "airline": "Air France",
            "departure_airport": "JFK",
            "arrival_airport": "CDG",
            "departure_time": f"{request.start_date}T08:30:00",
            "arrival_time": f"{request.start_date}T14:45:00",
            "price": 450.00,
            "duration": "8h 15m",
            "stops": 0,
            "status": "Available",
            "booking_class": "Economy"
        },
        {
            "flight_id": "BA456", 
            "airline": "British Airways",
            "departure_airport": "JFK",
            "arrival_airport": "LHR",
            "departure_time": f"{request.start_date}T12:15:00",
            "arrival_time": f"{request.start_date}T18:30:00", 
            "price": 520.00,
            "duration": "8h 15m",
            "stops": 0,
            "status": "Available",
            "booking_class": "Economy"
        }
    ]
    
    hotels = [
        {
            "hotel_id": "HTL001",
            "name": f"Grand {request.destination} Hotel",
            "location": f"{request.destination} City Center", 
            "rating": 4.5,
            "price_per_night": 180.00,
            "total_cost": 540.00,
            "amenities": ["WiFi", "Spa", "Restaurant", "Concierge"],
            "status": "Available",
            "checkin_time": "15:00",
            "checkout_time": "11:00"
        },
        {
            "hotel_id": "HTL002",
            "name": f"Boutique {request.destination} Inn", 
            "location": f"{request.destination} Historic District",
            "rating": 4.3,
            "price_per_night": 220.00,
            "total_cost": 660.00,
            "amenities": ["WiFi", "Gym", "Breakfast", "Rooftop"],
            "status": "Available",
            "checkin_time": "15:00", 
            "checkout_time": "11:00"
        }
    ]
    
    restaurants = [
        {
            "restaurant_id": "REST001",
            "name": "Le Gourmet Bistro",
            "cuisine": "French Fine Dining",
            "rating": 4.6,
            "avg_price_per_person": 65.00,
            "address": f"{request.destination} - Culinary District",
            "phone": "+33 1 42 96 89 70",
            "reservation_time": "19:30"
        },
        {
            "restaurant_id": "REST002", 
            "name": "Local Artisan Cafe",
            "cuisine": "Modern European",
            "rating": 4.4,
            "avg_price_per_person": 35.00,
            "address": f"{request.destination} - Arts Quarter", 
            "phone": "+33 1 45 63 78 92",
            "reservation_time": "12:30"
        },
        {
            "restaurant_id": "REST003",
            "name": "Heritage Brasserie",
            "cuisine": "Traditional Local", 
            "rating": 4.2,
            "avg_price_per_person": 45.00,
            "address": f"{request.destination} - Old Town",
            "phone": "+33 1 48 87 94 15",
            "reservation_time": "20:00"
        }
    ]
    
    activities = [
        {
            "activity_id": "ACT001",
            "name": f"{request.destination} Walking Tour",
            "category": "sightseeing", 
            "price": 25.00,
            "duration": "3 hours",
            "rating": 4.5,
            "location": f"{request.destination} Historic Center"
        },
        {
            "activity_id": "ACT002",
            "name": "Cultural Museum Visit",
            "category": "cultural",
            "price": 18.00, 
            "duration": "2 hours",
            "rating": 4.7,
            "location": f"{request.destination} Arts District"
        }
    ]
    
    total_cost = (
        flights[0]["price"] * request.travelers +
        hotels[0]["total_cost"] + 
        sum(r["avg_price_per_person"] * request.travelers for r in restaurants[:2]) +
        sum(a["price"] * request.travelers for a in activities)
    )
    
    response = {
        "success": True,
        "trip_id": f"DEMO_{datetime.now().timestamp()}",
        "destination": request.destination,
        "travelers": request.travelers, 
        "dates": {
            "start": request.start_date,
            "end": request.end_date
        },
        "budget": request.budget,
        "trip_data": {
            "basic_itinerary": {
                "flights": flights,
                "hotels": hotels,
                "restaurants": restaurants,
                "activities": activities
            },
            "comprehensive_itinerary": {
                "flights": flights,
                "hotels": hotels, 
                "restaurants": restaurants,
                "activities": activities
            }
        },
        "coordination": {
            "agents_used": ["flight-agent", "hotel-agent", "activity-agent"],
            "total_estimated_cost": total_cost,
            "api_sources": "Shell Hacks Demo System"
        },
        "status": "confirmed",
        "demo_ready": True
    }
    
    print(f"✅ INSTANT trip planned: ${total_cost:.2f} total")
    return response

# Mount frontend
try:
    frontend_path = "/Users/kyleprice/Desktop/shell_hacks/frontend"
    if os.path.exists(frontend_path):
        app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
        
        @app.get("/frontend/")
        async def serve_frontend():
            return FileResponse(f"{frontend_path}/index.html")
            
        print(f"✅ Frontend mounted from: {frontend_path}")
    else:
        print(f"⚠️ Frontend path not found: {frontend_path}")
        
except Exception as e:
    print(f"⚠️ Frontend mount error: {e}")

if __name__ == "__main__":
    print("🚀 EMERGENCY DEMO SYSTEM STARTING...")
    print("⚡ INSTANT responses, NO delays")  
    print("📍 Frontend: http://localhost:8000/frontend/")
    print("🔗 API: http://localhost:8000/api/plan-trip")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")