#!/usr/bin/env python3
"""
Test the full travel planning API to see if restaurants are included
"""
import asyncio
import httpx
from datetime import date, timedelta

async def test_travel_planning_api():
    """Test the full travel planning API"""
    
    # Prepare test data
    today = date.today()
    start_date = today + timedelta(days=30)  # 30 days from now
    end_date = start_date + timedelta(days=7)  # 7 day trip
    
    request_data = {
        "destination": "Paris, France",
        "departure_location": "New York, NY",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "travelers": 2,
        "budget": 5000,
        "preferences": ["luxury", "cultural"]
    }
    
    print("🔄 Testing travel planning API...")
    print(f"Request data: {request_data}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8001/api/plan-trip",
                json=request_data
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ API Response Keys: {list(result.keys())}")
                
                # Check if restaurants are in the response
                if "restaurants" in result:
                    restaurants = result["restaurants"]
                    print(f"🍽️ Restaurants found: {len(restaurants)}")
                    
                    for i, restaurant in enumerate(restaurants[:2]):
                        print(f"\nRestaurant {i+1}:")
                        print(f"  Name: {restaurant.get('name')}")
                        print(f"  Rating: {restaurant.get('rating')}")
                        print(f"  Address: {restaurant.get('address')}")
                        print(f"  Cuisine: {restaurant.get('cuisine_types')}")
                        print(f"  Cost: ${restaurant.get('estimated_cost')}")
                else:
                    print("❌ No 'restaurants' key found in response")
                    print(f"Available keys: {list(result.keys())}")
                
                # Check budget breakdown
                if "budget_breakdown" in result:
                    budget = result["budget_breakdown"]
                    print(f"\n💰 Budget Breakdown:")
                    for category, amount in budget.items():
                        print(f"  {category}: ${amount}")
                        
            else:
                print(f"❌ API call failed with status {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_travel_planning_api())
