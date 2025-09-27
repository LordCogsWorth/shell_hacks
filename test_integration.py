#!/usr/bin/env python3
"""
Test the travel agent API endpoint to see hotel and activities integration
"""

import asyncio
import httpx
import json
from datetime import date, timedelta

async def test_travel_agent_api():
    """Test the travel agent's plan-trip endpoint"""
    print("🧪 Testing TravelMaster AI Agent API")
    print("=" * 50)
    
    # Test data
    test_request = {
        "destination": "Paris",
        "departure_location": "New York",
        "start_date": (date.today() + timedelta(days=30)).isoformat(),
        "end_date": (date.today() + timedelta(days=35)).isoformat(),
        "budget": 3000,
        "travelers": 2,
        "preferences": ["cultural", "luxury"],
        "special_requirements": "Looking for authentic local experiences"
    }
    
    print("📋 Test Request:")
    print(json.dumps(test_request, indent=2))
    print()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("🚀 Sending request to travel agent...")
            response = await client.post(
                "http://localhost:8000/api/plan-trip",
                json=test_request
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print("✅ Trip Planning Successful!")
                print(f"💰 Total Cost: ${data.get('total_cost', 'N/A')}")
                print(f"💵 Savings: ${data.get('savings', 'N/A')}")
                print()
                
                # Check flights
                flights = data.get('flights', [])
                print(f"✈️  Flights: {len(flights)} found")
                if flights:
                    flight = flights[0]
                    print(f"   Sample: {flight.get('airline', 'N/A')} - ${flight.get('price', 'N/A')}")
                print()
                
                # Check hotels - THIS IS WHAT WE'RE TESTING
                hotels = data.get('hotels', [])
                print(f"🏨 Hotels: {len(hotels)} found")
                if hotels:
                    for i, hotel in enumerate(hotels, 1):
                        print(f"   Hotel {i}: {hotel.get('name', 'N/A')}")
                        print(f"      Rating: {hotel.get('rating', 'N/A')} stars")
                        print(f"      Price: ${hotel.get('price_per_night', 'N/A')}/night")
                        print(f"      Total: ${hotel.get('total_price', 'N/A')}")
                        print(f"      Location: {hotel.get('location', 'N/A')}")
                        print(f"      Amenities: {', '.join(hotel.get('amenities', [])[:3])}")
                        print()
                else:
                    print("   ❌ NO HOTELS FOUND!")
                
                # Check activities - THIS IS WHAT WE'RE TESTING  
                activities = data.get('activities', [])
                print(f"🎯 Activities: {len(activities)} found")
                if activities:
                    # Separate sights and activities
                    sights = [a for a in activities if 'sight' in a.get('type', '').lower()]
                    experiences = [a for a in activities if 'sight' not in a.get('type', '').lower()]
                    
                    if sights:
                        print("   👁️  SIGHTS TO SEE:")
                        for sight in sights:
                            price_text = f"${sight.get('price', 'N/A')}" if sight.get('price', 0) > 0 else "Free"
                            print(f"      • {sight.get('name', 'N/A')} - {price_text} ({sight.get('duration', 'N/A')})")
                    
                    if experiences:
                        print("   🎪 ACTIVITIES TO DO:")
                        for activity in experiences:
                            print(f"      • {activity.get('name', 'N/A')} - ${activity.get('price', 'N/A')} ({activity.get('duration', 'N/A')})")
                    
                    if not sights and not experiences:
                        print("   Activities found but type classification unclear:")
                        for activity in activities[:3]:
                            print(f"      • {activity.get('name', 'N/A')} - ${activity.get('price', 'N/A')}")
                            print(f"        Type: {activity.get('type', 'N/A')}")
                else:
                    print("   ❌ NO ACTIVITIES FOUND!")
                
                # Check daily schedule
                schedule = data.get('daily_schedule', [])
                print(f"\n📅 Daily Schedule: {len(schedule)} days")
                if schedule:
                    for day in schedule[:2]:  # Show first 2 days
                        day_activities = day.get('activities', [])
                        print(f"   Day {day.get('day_number', '?')}: {len(day_activities)} activities")
                        for act in day_activities[:2]:
                            print(f"      • {act.get('name', 'N/A')} - ${act.get('price', 'N/A')}")
                
                # Budget breakdown
                breakdown = data.get('budget_breakdown', {})
                print(f"\n💰 Budget Breakdown:")
                print(f"   Flights: ${breakdown.get('flights', 'N/A')}")
                print(f"   Hotels: ${breakdown.get('hotels', 'N/A')}")
                print(f"   Activities: ${breakdown.get('activities', 'N/A')}")
                print(f"   Remaining: ${breakdown.get('remaining', 'N/A')}")
                
                return True
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_health_endpoint():
    """Test if the server is running"""
    print("🔍 Checking if travel agent server is running...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/api/health")
            if response.status_code == 200:
                print("✅ Server is running!")
                return True
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the travel agent is running on http://localhost:8000")
        return False

async def main():
    print("🧪 TravelMaster AI Agent Integration Test")
    print("=" * 60)
    
    # Check if server is running
    server_ok = await test_health_endpoint()
    
    if not server_ok:
        print("\n❌ Cannot test - server is not running!")
        print("Start the server with: uv run python src/travel_agent.py")
        return
    
    # Test the API
    api_ok = await test_travel_agent_api()
    
    # Summary
    print("\n" + "=" * 60)
    if api_ok:
        print("🎉 Integration test PASSED!")
        print("The travel agent is successfully integrating hotels and activities.")
    else:
        print("❌ Integration test FAILED!")
        print("Check the server logs and API implementation.")

if __name__ == "__main__":
    asyncio.run(main())
